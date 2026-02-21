from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import json
import os
import logging
from datetime import datetime
from gmail_service import GmailMonitor
import threading
import time

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
socketio = SocketIO(app, cors_allowed_origins="*")

# Variables globales
monitor = None
netflix_emails = []
monitoring_active = False
monitoring_thread = None

def load_accounts():
    """Carga las cuentas desde variable de entorno o archivo de configuración"""
    # Intentar cargar desde variable de entorno primero (para deployment en nube)
    # Soporta EMAIL_ACCOUNTS (nuevo) y GMAIL_ACCOUNTS
    env_accounts = os.environ.get('EMAIL_ACCOUNTS') or os.environ.get('GMAIL_ACCOUNTS')
    if env_accounts:
        try:
            accounts = json.loads(env_accounts)
            logger.info(f"Cuentas cargadas desde variable de entorno: {len(accounts)}")
            return accounts
        except json.JSONDecodeError as e:
            logger.error(f"Error al parsear EMAIL_ACCOUNTS/GMAIL_ACCOUNTS desde variable de entorno: {str(e)}")
    
    # Fallback: Intentar cargar desde archivo
    try:
        with open('accounts.json', 'r') as f:
            data = json.load(f)
            accounts = data.get('accounts', [])
            logger.info(f"Cuentas cargadas desde accounts.json: {len(accounts)}")
            return accounts
    except FileNotFoundError:
        logger.warning("Archivo accounts.json no encontrado. Usa EMAIL_ACCOUNTS o GMAIL_ACCOUNTS env var o crea accounts.json")
        return []
    except Exception as e:
        logger.error(f"Error al cargar accounts.json: {str(e)}")
        return []

def load_settings():
    """Carga la configuración desde el archivo de configuración"""
    try:
        with open('settings.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning("Archivo settings.json no encontrado, usando valores por defecto")
        return {
            'check_interval': 30,  # 30 segundos para detección casi en tiempo real
            'days_back': 7,
            'auto_mark_read': False
        }
    except Exception as e:
        logger.error(f"Error al cargar settings.json: {str(e)}")
        return {
            'check_interval': 30,
            'days_back': 7,
            'auto_mark_read': False
        }

def monitoring_loop():
    """
    Loop de monitoreo en segundo plano.
    Intenta usar IMAP IDLE (push en tiempo real).
    Si IDLE no funciona, usa polling con el intervalo configurado.
    """
    global netflix_emails, monitoring_active

    settings = load_settings()
    check_interval = settings.get('check_interval', 30)
    days_back = settings.get('days_back', 7)

    logger.info(f"Iniciando loop de monitoreo (intervalo fallback: {check_interval}s, días: {days_back})")

    # ── Carga inicial completa ──────────────────────────────────────────────
    try:
        if monitor:
            logger.info("Carga inicial de correos de Netflix...")
            netflix_emails = monitor.fetch_all_netflix_emails(days_back=days_back)
            logger.info(f"Carga inicial completada: {len(netflix_emails)} correos encontrados")
            socketio.emit('emails_updated', {
                'total': len(netflix_emails),
                'timestamp': datetime.now().isoformat()
            })
    except Exception as e:
        logger.error(f"Error en carga inicial: {str(e)}")

    # ── Loop principal con IMAP IDLE ────────────────────────────────────────
    from gmail_service import IMAPService

    idle_services = {}   # email_address → IMAPService con conexión persistente

    def open_idle_connections():
        """Abre conexiones persistentes para IDLE en todas las cuentas."""
        accounts = load_accounts()
        for acc in accounts:
            addr = acc.get('email')
            pwd  = acc.get('password')
            if not addr or not pwd or addr in idle_services:
                continue
            try:
                svc = IMAPService(email_address=addr, password=pwd)
                svc.connect()
                svc.mail.select("INBOX")
                idle_services[addr] = svc
                logger.info(f"Conexión IDLE abierta para {addr}")
            except Exception as e:
                logger.warning(f"No se pudo abrir conexión IDLE para {addr}: {e}")

    open_idle_connections()

    last_full_check = time.time()
    FULL_CHECK_EVERY = 300   # Forzar re-verificación completa cada 5 min como respaldo

    while monitoring_active:
        try:
            new_found = False

            # ── Escuchar IDLE en cada cuenta ────────────────────────────────
            for addr, svc in list(idle_services.items()):
                try:
                    got_notification = svc.wait_for_new_email(timeout=check_interval)
                    if got_notification:
                        logger.info(f"[{addr}] Notificación IDLE recibida — buscando correos nuevos...")
                        recent = svc.fetch_recent_netflix_emails(minutes_back=15)
                        if recent:
                            old_ids = {e['id'] for e in netflix_emails}
                            truly_new = [e for e in recent if e['id'] not in old_ids]
                            if truly_new:
                                netflix_emails = truly_new + netflix_emails
                                netflix_emails.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
                                logger.info(f"[{addr}] {len(truly_new)} correos nuevos encontrados por IDLE")
                                socketio.emit('new_emails', {
                                    'count': len(truly_new),
                                    'emails': truly_new
                                })
                                socketio.emit('emails_updated', {
                                    'total': len(netflix_emails),
                                    'timestamp': datetime.now().isoformat()
                                })
                                new_found = True
                except Exception as e:
                    logger.warning(f"[{addr}] Error en IDLE, reconectando: {e}")
                    try:
                        svc.disconnect()
                    except:
                        pass
                    del idle_services[addr]
                    # Intentar reconectar
                    try:
                        accounts = load_accounts()
                        acc_data = next((a for a in accounts if a.get('email') == addr), None)
                        if acc_data:
                            new_svc = IMAPService(email_address=addr, password=acc_data['password'])
                            new_svc.connect()
                            new_svc.mail.select("INBOX")
                            idle_services[addr] = new_svc
                            logger.info(f"[{addr}] Reconectado exitosamente")
                    except Exception as e2:
                        logger.error(f"[{addr}] No se pudo reconectar: {e2}")

            # ── Si no había conexiones IDLE, esperar el intervalo normal ────
            if not idle_services:
                logger.info("Sin conexiones IDLE activas, usando polling normal...")
                time.sleep(check_interval)

            # ── Verificación completa periódica (cada 5 min) ─────────────────
            if time.time() - last_full_check >= FULL_CHECK_EVERY:
                logger.info("Ejecutando verificación completa periódica...")
                if monitor:
                    all_emails = monitor.fetch_all_netflix_emails(days_back=days_back)
                    old_ids = {e['id'] for e in netflix_emails}
                    truly_new = [e for e in all_emails if e['id'] not in old_ids]
                    if truly_new:
                        netflix_emails = all_emails
                        logger.info(f"Verificación completa encontró {len(truly_new)} correos nuevos")
                        socketio.emit('new_emails', {
                            'count': len(truly_new),
                            'emails': truly_new
                        })
                    else:
                        netflix_emails = all_emails
                    socketio.emit('emails_updated', {
                        'total': len(netflix_emails),
                        'timestamp': datetime.now().isoformat()
                    })
                last_full_check = time.time()

        except Exception as e:
            logger.error(f"Error en loop de monitoreo: {str(e)}")
            time.sleep(check_interval)

    # Cerrar conexiones IDLE al detener
    for addr, svc in idle_services.items():
        try:
            svc.disconnect()
        except:
            pass
    logger.info("Loop de monitoreo detenido.")


@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/api/accounts')
def get_accounts():
    """Obtiene la lista de cuentas configuradas (sin contraseñas)"""
    accounts = load_accounts()
    safe_accounts = [{'email': acc.get('email', 'N/A')} for acc in accounts]
    return jsonify({
        'success': True,
        'accounts': safe_accounts,
        'total': len(safe_accounts)
    })

@app.route('/api/settings')
def get_settings():
    """Obtiene la configuración actual"""
    settings = load_settings()
    return jsonify({
        'success': True,
        'settings': settings
    })

@app.route('/api/settings', methods=['POST'])
def update_settings():
    """Actualiza la configuración"""
    try:
        new_settings = request.json
        
        with open('settings.json', 'w') as f:
            json.dump(new_settings, f, indent=2)
        
        return jsonify({
            'success': True,
            'message': 'Configuración actualizada correctamente'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/emails')
def get_emails():
    """Obtiene todos los correos de Netflix filtrados"""
    email_type = request.args.get('type', None)
    account = request.args.get('account', None)
    
    filtered_emails = netflix_emails
    
    # Filtrar por tipo si se especifica
    if email_type:
        filtered_emails = [e for e in filtered_emails if e['type'] == email_type]
    
    # Filtrar por cuenta si se especifica
    if account:
        filtered_emails = [e for e in filtered_emails if e['account'] == account]
    
    return jsonify({
        'success': True,
        'emails': filtered_emails,
        'total': len(filtered_emails),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/check', methods=['POST'])
def check_emails():
    """Fuerza una verificación manual de correos"""
    global netflix_emails
    
    try:
        settings = load_settings()
        days_back = settings.get('days_back', 7)
        
        if monitor:
            netflix_emails = monitor.fetch_all_netflix_emails(days_back=days_back)
            
            return jsonify({
                'success': True,
                'message': f'Se encontraron {len(netflix_emails)} correos de Netflix',
                'total': len(netflix_emails),
                'emails': netflix_emails
            })
        else:
            return jsonify({
                'success': False,
                'error': 'El monitor no está inicializado'
            }), 500
    
    except Exception as e:
        logger.error(f"Error al verificar correos: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/start', methods=['POST'])
def start_monitoring():
    """Inicia el monitoreo automático"""
    global monitoring_active, monitoring_thread, monitor
    
    if monitoring_active:
        return jsonify({
            'success': False,
            'message': 'El monitoreo ya está activo'
        })
    
    try:
        # Cargar cuentas
        accounts = load_accounts()
        
        if not accounts:
            return jsonify({
                'success': False,
                'error': 'No hay cuentas configuradas'
            }), 400
        
        # Inicializar monitor de Gmail
        monitor = GmailMonitor(accounts)
        
        # Iniciar thread de monitoreo
        monitoring_active = True
        monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
        monitoring_thread.start()
        
        logger.info("Monitoreo iniciado correctamente")
        
        return jsonify({
            'success': True,
            'message': 'Monitoreo iniciado correctamente',
            'accounts': len(accounts)
        })
    
    except Exception as e:
        monitoring_active = False
        logger.error(f"Error al iniciar monitoreo: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stop', methods=['POST'])
def stop_monitoring():
    """Detiene el monitoreo automático"""
    global monitoring_active
    
    if not monitoring_active:
        return jsonify({
            'success': False,
            'message': 'El monitoreo no está activo'
        })
    
    monitoring_active = False
    logger.info("Monitoreo detenido")
    
    return jsonify({
        'success': True,
        'message': 'Monitoreo detenido correctamente'
    })

@app.route('/api/stats')
def get_stats():
    """Obtiene estadísticas de los correos"""
    stats = {
        'total': len(netflix_emails),
        'by_type': {},
        'by_account': {},
        'monitoring_active': monitoring_active
    }
    
    for email in netflix_emails:
        # Contar por tipo
        email_type = email.get('type', 'unknown')
        stats['by_type'][email_type] = stats['by_type'].get(email_type, 0) + 1
        
        # Contar por cuenta
        account = email.get('account', 'unknown')
        stats['by_account'][account] = stats['by_account'].get(account, 0) + 1
    
    return jsonify({
        'success': True,
        'stats': stats
    })

@socketio.on('connect')
def handle_connect():
    """Maneja nuevas conexiones WebSocket"""
    logger.info(f"Cliente conectado")
    emit('connected', {
        'message': 'Conectado al servidor',
        'monitoring_active': monitoring_active,
        'total_emails': len(netflix_emails)
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Maneja desconexiones WebSocket"""
    logger.info("Cliente desconectado")

@socketio.on('request_update')
def handle_request_update():
    """Maneja solicitudes de actualización desde el cliente"""
    emit('emails_updated', {
        'total': len(netflix_emails),
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    logger.info("Iniciando servidor Netflix Codes Monitor...")
    
    # Cargar configuración inicial
    accounts_config = load_accounts()
    settings = load_settings()
    
    logger.info(f"Cuentas configuradas: {len(accounts_config)}")
    logger.info(f"Configuración: {settings}")
    
    # Auto-iniciar monitor si hay cuentas
    if accounts_config:
        try:
            from gmail_service import GmailMonitor
            # Inicializar monitor global
            monitor = GmailMonitor(accounts_config)
            
            # Iniciar monitoreo automático
            monitoring_active = True
            monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
            monitoring_thread.start()
            logger.info("Auto-monitoreo iniciado al arrancar la aplicación")
        except Exception as e:
            logger.error(f"Error al auto-iniciar monitoreo: {str(e)}")
    
    # Iniciar servidor
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True)
