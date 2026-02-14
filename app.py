from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import json
import os
import logging
from datetime import datetime
from outlook_service import OutlookMonitor
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
    # Soporta EMAIL_ACCOUNTS (nuevo) y OUTLOOK_ACCOUNTS (compatibilidad)
    env_accounts = os.environ.get('EMAIL_ACCOUNTS') or os.environ.get('OUTLOOK_ACCOUNTS')
    if env_accounts:
        try:
            accounts = json.loads(env_accounts)
            logger.info(f"Cuentas cargadas desde variable de entorno: {len(accounts)}")
            return accounts
        except json.JSONDecodeError as e:
            logger.error(f"Error al parsear EMAIL_ACCOUNTS/OUTLOOK_ACCOUNTS desde variable de entorno: {str(e)}")
    
    # Fallback: Intentar cargar desde archivo
    try:
        with open('accounts.json', 'r') as f:
            data = json.load(f)
            accounts = data.get('accounts', [])
            logger.info(f"Cuentas cargadas desde accounts.json: {len(accounts)}")
            return accounts
    except FileNotFoundError:
        logger.warning("Archivo accounts.json no encontrado. Usa EMAIL_ACCOUNTS o OUTLOOK_ACCOUNTS env var o crea accounts.json")
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
            'check_interval': 300,  # 5 minutos
            'days_back': 7,
            'auto_mark_read': False
        }
    except Exception as e:
        logger.error(f"Error al cargar settings.json: {str(e)}")
        return {
            'check_interval': 300,
            'days_back': 7,
            'auto_mark_read': False
        }

def monitoring_loop():
    """Loop de monitoreo en segundo plano"""
    global netflix_emails, monitoring_active
    
    settings = load_settings()
    check_interval = settings.get('check_interval', 300)
    days_back = settings.get('days_back', 7)
    
    logger.info(f"Iniciando loop de monitoreo (intervalo: {check_interval}s, días: {days_back})")
    
    while monitoring_active:
        try:
            logger.info("Verificando correos de Netflix...")
            
            if monitor:
                new_emails = monitor.fetch_all_netflix_emails(days_back=days_back)
                
                # Detectar nuevos correos
                old_ids = {email['id'] for email in netflix_emails}
                new_ids = {email['id'] for email in new_emails}
                truly_new = new_ids - old_ids
                
                if truly_new:
                    logger.info(f"Se encontraron {len(truly_new)} nuevos correos de Netflix")
                    socketio.emit('new_emails', {
                        'count': len(truly_new),
                        'emails': [e for e in new_emails if e['id'] in truly_new]
                    })
                
                netflix_emails = new_emails
                
                # Emitir actualización a todos los clientes
                socketio.emit('emails_updated', {
                    'total': len(netflix_emails),
                    'timestamp': datetime.now().isoformat()
                })
            
        except Exception as e:
            logger.error(f"Error en loop de monitoreo: {str(e)}")
        
        # Esperar el intervalo configurado
        time.sleep(check_interval)

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
        
        # Inicializar monitor
        monitor = OutlookMonitor(accounts)
        
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
    logger.info("Iniciando servidor Flask...")
    
    # Cargar configuración inicial
    accounts = load_accounts()
    settings = load_settings()
    
    logger.info(f"Cuentas configuradas: {len(accounts)}")
    logger.info(f"Configuración: {settings}")
    
    # Iniciar servidor
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=True, allow_unsafe_werkzeug=True)
