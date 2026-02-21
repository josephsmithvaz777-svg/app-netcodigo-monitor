import imaplib
import email
from email.header import decode_header
import re
from datetime import datetime, timedelta
from typing import List, Dict
import logging
from email.utils import parsedate_to_datetime
import time

logger = logging.getLogger(__name__)

class IMAPService:
    """Servicio para conectar y leer correos de Gmail vía IMAP"""
    
    # Configuración de servidor IMAP de Gmail
    IMAP_SERVER = 'imap.gmail.com'
    IMAP_PORT = 993
    
    # Patrones para identificar correos de Netflix
    NETFLIX_PATTERNS = {
        'codigo_inicio': [
            r'c[oó]digo de inicio',
            r'sign-in code',
            r'verification code',
            r'c[oó]digo de verificaci[oó]n'
        ],
        'codigo_temporal': [
            r'c[oó]digo de acceso temporal',
            r'c[oó]digo temporal',
            r'obtener c[oó]digo',
            r'temporary code',
            r'temporary access code',
            r'one-time code',
            r'c[oó]digo de un solo uso'
        ],
        'actualizacion_hogar': [
            r'actualizaci[oó]n de hogar',
            r'actualizar tu hogar',
            r'confirmar hogar',
            r'household update',
            r'update your netflix household',
            r'manage your household',
            r'administra tu hogar',
            r'¿solicitaste actualizar',
            r'actualizar.*?hogar'
        ]
    }
    
    def __init__(self, email_address: str, password: str):
        """
        Inicializa el servicio IMAP para Gmail
        
        Args:
            email_address: Dirección de correo de Gmail
            password: Contraseña de aplicación de Gmail
        """
        self.email_address = email_address
        self.password = password
        self.mail = None
        self.imap_server = self.IMAP_SERVER
        self.imap_port = self.IMAP_PORT
        
    def connect(self):
        """Conecta al servidor IMAP"""
        try:
            logger.info(f"Conectando a Gmail ({self.imap_server}:{self.imap_port}) para {self.email_address}")
            self.mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            self.mail.login(self.email_address, self.password)
            logger.info(f"Conectado exitosamente a Gmail: {self.email_address}")
            return True
        except Exception as e:
            logger.error(f"Error al conectar a Gmail ({self.email_address}): {str(e)}")
            raise
    
    def disconnect(self):
        """Desconecta del servidor IMAP"""
        if self.mail:
            try:
                self.mail.close()
                self.mail.logout()
                logger.info(f"Desconectado de {self.email_address}")
            except:
                pass
    
    def _decode_mime_words(self, s):
        """Decodifica palabras MIME en el encabezado"""
        if s is None:
            return ""
        decoded_fragments = decode_header(s)
        result = []
        for fragment, encoding in decoded_fragments:
            if isinstance(fragment, bytes):
                if encoding:
                    try:
                        result.append(fragment.decode(encoding))
                    except:
                        result.append(fragment.decode('utf-8', errors='ignore'))
                else:
                    result.append(fragment.decode('utf-8', errors='ignore'))
            else:
                result.append(str(fragment))
        return ''.join(result)
    
    def _get_email_body(self, msg):
        """Extrae el cuerpo del correo, priorizando HTML para una mejor visualización"""
        html_body = ""
        plain_body = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                if "attachment" in content_disposition:
                    continue
                    
                if content_type == "text/html":
                    try:
                        html_body = part.get_payload(decode=True).decode()
                    except:
                        pass
                elif content_type == "text/plain":
                    try:
                        plain_body = part.get_payload(decode=True).decode()
                    except:
                        pass
        else:
            try:
                content_type = msg.get_content_type()
                payload = msg.get_payload(decode=True).decode()
                if content_type == "text/html":
                    html_body = payload
                else:
                    plain_body = payload
            except:
                pass
        
        # Priorizar HTML para el visor original
        return html_body if html_body else plain_body
    
    def _classify_email(self, subject: str, body: str) -> str:
        """
        Clasifica el correo según el tipo de código de Netflix
        
        Returns:
            'codigo_inicio', 'codigo_temporal', 'actualizacion_hogar' o None
        """
        text_to_search = (subject + " " + body).lower()
        
        for email_type, patterns in self.NETFLIX_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_to_search, re.IGNORECASE):
                    return email_type
        
        return None
    
    def _extract_code_or_link(self, body: str, email_type: str) -> str:
        """
        Extrae el código o link según el tipo de correo usando BeautifulSoup para mayor precisión
        """
        if not body:
            return ""

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(body, 'html.parser')
        
        # 1. Caso: Código de Inicio (Numérico)
        if email_type == 'codigo_inicio':
            # Primero intentar extraer del texto plano para evitar tags intermedios
            text_content = soup.get_text(separator=' ')
            patterns = [
                r'(?:código|code).*?(?:iniciar sesión|sign-?in|login).*?(\d{4,8})',
                r'(?:iniciar sesión|sign-?in|login).*?(?:código|code).*?(\d{4,8})',
                r'(?:ingresa|enter).*?(?:este|this).*?(?:código|code).*?(\d{4,8})',
                r'(?:para|to).*?(?:iniciar sesión|sign in).*?(\d{4,8})',
            ]
            for pattern in patterns:
                match = re.search(pattern, text_content, re.IGNORECASE | re.DOTALL)
                if match:
                    return match.group(1)
            
            # Fallback a 4 dígitos aislados si hay contexto de login
            if re.search(r'sign-?in|iniciar sesión', text_content, re.IGNORECASE):
                match = re.search(r'\b(\d{4,6})\b', text_content)
                if match:
                    return match.group(1)

        # 2. Caso: Links (Hogar o Temporal)
        # Prioridad absoluta: Buscar el botón rojo de Netflix o links con estilo de botón
        # Netflix suele usar tablas con background color o estilos inline para los botones
        
        # Buscar todos los enlaces
        all_links = soup.find_all('a', href=True)
        
        # Filtrar por prioridad
        primary_link = None
        
        # Prioridad 1: Enlaces que contienen palabras clave en su texto (ej: "Sí, la envié yo", "Obtener código")
        button_keywords = [
            'sí, la envié yo', 'si, la envie yo', 'obtener código', 'obtener codigo', 
            'get code', 'verify', 'update', 'actualizar', 'confirmar', 'yes, this was me'
        ]
        
        for link in all_links:
            link_text = link.get_text().lower().strip()
            link_href = link['href']
            
            # Solo procesar links de netflix.com
            if 'netflix.com' not in link_href:
                continue
                
            # Evitar links de ayuda o legales
            if any(word in link_href.lower() for word in ['help', 'privacy', 'unsubscribe', 'terms', 'contact']):
                continue

            # Si el texto coincide con un botón, es casi seguro que es el correcto
            if any(keyword in link_text for keyword in button_keywords):
                primary_link = link_href
                break
        
        # Prioridad 2: Si no se encontró por texto, buscar en los patrones de URL (nmv, access, household)
        if not primary_link:
            patterns = []
            if email_type == 'actualizacion_hogar':
                patterns = [r'/household/', r'/update-household/', r'/update-primary-location/']
            elif email_type == 'codigo_temporal':
                patterns = [r'/temporary-access/', r'/access/', r'/otp/', r'/nmv/']
                
            for link in all_links:
                link_href = link['href']
                if 'netflix.com' in link_href:
                    if any(re.search(p, link_href, re.IGNORECASE) for p in patterns):
                        primary_link = link_href
                        break

        # Prioridad 3: Último recurso, el primer link de netflix que no sea basura
        if not primary_link:
            for link in all_links:
                link_href = link['href']
                if 'netflix.com' in link_href and not any(word in link_href.lower() for word in ['help', 'privacy', 'unsubscribe']):
                    primary_link = link_href
                    break
                    
        return primary_link if primary_link else ""
    
    def fetch_netflix_emails(self, days_back: int = 7) -> List[Dict]:
        """
        Obtiene correos de Netflix de los últimos N días
        
        Args:
            days_back: Número de días hacia atrás para buscar
            
        Returns:
            Lista de diccionarios con información de los correos
        """
        if not self.mail:
            self.connect()
        
        # Seleccionar la bandeja de entrada
        self.mail.select("INBOX")
        
        # Calcular fecha de búsqueda (formato IMAP: 17-Feb-2026)
        # Usamos days_back + 1 para asegurar que no se pierdan correos del borde del día
        search_date = (datetime.now() - timedelta(days=days_back + 1)).strftime("%d-%b-%Y")
        
        logger.info(f"[{self.email_address}] Buscando desde {search_date} (días: {days_back})")
        
        try:
            # Buscar correos de Netflix de forma más eficiente en Gmail
            # X-GM-RAW nos permite buscar con operadores tipo web (más potente)
            # Usamos una búsqueda más amplia (un día extra atrás) para evitar problemas de zona horaria
            search_query = f'from:netflix.com after:{(datetime.now() - timedelta(days=days_back + 1)).strftime("%Y/%m/%d")}'
            logger.info(f"[{self.email_address}] Buscando con query: {search_query}")
            status, messages = self.mail.search(None, 'X-GM-RAW', search_query)
        except:
            # Fallback a búsqueda IMAP estándar si X-GM-RAW falla
            search_date = (datetime.now() - timedelta(days=days_back + 1)).strftime("%d-%b-%Y")
            status, messages = self.mail.search(None, f'(FROM "netflix.com" SINCE {search_date})')
        
        if status != "OK" or not messages[0]:
            # Segundo intento: buscar por palabra "Netflix"
            logger.info(f"[{self.email_address}] Reintentando búsqueda general...")
            search_date = (datetime.now() - timedelta(days=days_back + 1)).strftime("%d-%b-%Y")
            status, messages = self.mail.search(None, f'(SUBJECT "Netflix" SINCE {search_date})')
        
        if status != "OK":
            logger.warning(f"[{self.email_address}] Error al ejecutar búsqueda IMAP")
            return []
        
        email_ids = messages[0].split()
        logger.info(f"[{self.email_address}] Encontrados {len(email_ids)} correos potenciales")
        netflix_emails = []
        
        # Procesar cada correo
        for email_id in email_ids:
            try:
                status, msg_data = self.mail.fetch(email_id, "(RFC822)")
                
                if status != "OK":
                    continue
                
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        
                        # Decodificar asunto y remitente
                        subject = self._decode_mime_words(msg["Subject"])
                        from_address = self._decode_mime_words(msg["From"])
                        
                        # Estrategia para obtener el destinatario real
                        # Priorizamos el "To" del header porque suele contener la cuenta original (digitalacc09...)
                        to_address = self._decode_mime_words(msg["To"])
                        
                        # Si no hay, probamos otros (fallback)
                        if not to_address:
                            to_address = self._decode_mime_words(msg["Delivered-To"])
                        if not to_address:
                            to_address = self._decode_mime_words(msg["X-Forwarded-To"])
                        
                        # Extraer fecha real para ordenamiento
                        date_str = msg["Date"]
                        try:
                            dt = parsedate_to_datetime(date_str)
                            timestamp = dt.timestamp()
                        except:
                            timestamp = 0
                        
                        # Obtener cuerpo
                        body = self._get_email_body(msg)
                        
                        # Clasificar el correo
                        email_type = self._classify_email(subject, body)
                        
                        if email_type:
                            # Extraer código o link según el tipo
                            code = self._extract_code_or_link(body, email_type)
                            
                            netflix_emails.append({
                                'id': email_id.decode(),
                                'subject': subject,
                                'from': from_address,
                                'to': to_address,
                                'date': date_str,
                                'timestamp': timestamp,
                                'type': email_type,
                                'code': code,
                                'body_preview': body[:200] if body else "",
                                'body_full': body,
                                'account': self.email_address
                            })
                            
                            logger.info(f"Correo de Netflix encontrado: {subject} - Tipo: {email_type}")
            
            except Exception as e:
                logger.error(f"Error al procesar correo {email_id}: {str(e)}")
                continue
        
        return netflix_emails
    
    def mark_as_read(self, email_id: str):
        """Marca un correo como leído"""
        try:
            self.mail.store(email_id, '+FLAGS', '\\Seen')
            logger.info(f"Correo {email_id} marcado como leído")
        except Exception as e:
            logger.error(f"Error al marcar correo como leído: {str(e)}")

    def wait_for_new_email(self, timeout: int = 25) -> bool:
        """
        Usa IMAP IDLE para esperar notificaciones push de Gmail.
        Retorna True si llegó un correo nuevo, False si fue timeout.
        El timeout máximo recomendado es 29 min (Gmail cierra IDLE a los 30 min).
        """
        try:
            # Enviar comando IDLE
            tag = self.mail._new_tag()
            self.mail.send(f'{tag.decode()} IDLE\r\n'.encode())
            
            # Leer respuesta de confirmación "+ idling"
            resp = self.mail.readline()
            logger.debug(f"[{self.email_address}] IDLE iniciado: {resp.decode(errors='ignore').strip()}")
            
            # Esperar datos dentro del timeout
            import select
            sock = self.mail.socket()
            readable, _, _ = select.select([sock], [], [], timeout)
            
            # Salir de IDLE
            self.mail.send(b'DONE\r\n')
            
            if readable:
                # Hay datos → llegó algo nuevo (EXISTS, FETCH, EXPUNGE…)
                line = self.mail.readline()
                logger.info(f"[{self.email_address}] IDLE notificación: {line.decode(errors='ignore').strip()}")
                # Consumir respuesta final del servidor
                try:
                    self.mail.readline()
                except:
                    pass
                return True
            else:
                # Timeout normal, sin notificación
                try:
                    self.mail.readline()
                except:
                    pass
                return False

        except Exception as e:
            logger.warning(f"[{self.email_address}] IMAP IDLE no soportado o error: {str(e)}")
            return False

    def fetch_recent_netflix_emails(self, minutes_back: int = 10) -> List[Dict]:
        """
        Búsqueda rápida sólo de correos de los últimos N minutos.
        Útil para el chequeo tras una notificación IDLE.
        """
        if not self.mail:
            self.connect()

        self.mail.select("INBOX")
        search_date = (datetime.now() - timedelta(minutes=minutes_back)).strftime("%d-%b-%Y")

        try:
            search_query = f'from:netflix.com after:{(datetime.now() - timedelta(minutes=minutes_back)).strftime("%Y/%m/%d")}'
            status, messages = self.mail.search(None, 'X-GM-RAW', search_query)
        except Exception:
            status, messages = self.mail.search(None, f'(FROM "netflix.com" SINCE {search_date})')

        if status != "OK" or not messages[0]:
            return []

        email_ids = messages[0].split()
        netflix_emails = []

        for email_id in email_ids:
            try:
                status, msg_data = self.mail.fetch(email_id, "(RFC822)")
                if status != "OK":
                    continue
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject = self._decode_mime_words(msg["Subject"])
                        from_address = self._decode_mime_words(msg["From"])
                        to_address = self._decode_mime_words(msg["To"])
                        if not to_address:
                            to_address = self._decode_mime_words(msg["Delivered-To"])
                        if not to_address:
                            to_address = self._decode_mime_words(msg["X-Forwarded-To"])
                        date_str = msg["Date"]
                        try:
                            dt = parsedate_to_datetime(date_str)
                            timestamp = dt.timestamp()
                        except:
                            timestamp = 0
                        body = self._get_email_body(msg)
                        email_type = self._classify_email(subject, body)
                        if email_type:
                            code = self._extract_code_or_link(body, email_type)
                            netflix_emails.append({
                                'id': email_id.decode(),
                                'subject': subject,
                                'from': from_address,
                                'to': to_address,
                                'date': date_str,
                                'timestamp': timestamp,
                                'type': email_type,
                                'code': code,
                                'body_preview': body[:200] if body else "",
                                'body_full': body,
                                'account': self.email_address
                            })
            except Exception as e:
                logger.error(f"Error al procesar correo reciente {email_id}: {str(e)}")
                continue

        return netflix_emails


class GmailMonitor:
    """Monitor para múltiples cuentas de Gmail"""
    
    def __init__(self, accounts: List[Dict[str, str]]):
        """
        Inicializa el monitor con múltiples cuentas de Gmail
        
        Args:
            accounts: Lista de diccionarios con 'email' y 'password'
        """
        self.accounts = accounts
        self.services = []
        
    def fetch_all_netflix_emails(self, days_back: int = 7) -> List[Dict]:
        """
        Obtiene correos de Netflix de todas las cuentas de Gmail configuradas
        
        Args:
            days_back: Número de días hacia atrás para buscar
            
        Returns:
            Lista consolidada de todos los correos de Netflix
        """
        all_emails = []
        
        for account in self.accounts:
            email_address = account.get('email')
            password = account.get('password')
            
            if not email_address or not password:
                logger.warning(f"Cuenta sin email o password: {account}")
                continue
            
            try:
                service = IMAPService(
                    email_address=email_address,
                    password=password
                )
                service.connect()
                
                emails = service.fetch_netflix_emails(days_back)
                all_emails.extend(emails)
                
                service.disconnect()
                
            except Exception as e:
                logger.error(f"Error al procesar cuenta de Gmail {email_address}: {str(e)}")
                continue
        
        # Ordenar por timestamp numérico (más recientes primero)
        all_emails.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
        
        return all_emails

# Mantener compatibilidad con código existente
EmailMonitor = GmailMonitor
