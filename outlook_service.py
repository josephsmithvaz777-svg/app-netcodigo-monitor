import imaplib
import email
from email.header import decode_header
import re
from datetime import datetime, timedelta
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class IMAPService:
    """Servicio para conectar y leer correos de Gmail vía IMAP"""
    
    # Configuración de servidor IMAP de Gmail
    IMAP_SERVER = 'imap.gmail.com'
    IMAP_PORT = 993
    
    # Patrones para identificar correos de Netflix
    NETFLIX_PATTERNS = {
        'codigo_inicio': [
            r'Código de inicio',
            r'Sign-in code',
            r'verification code',
            r'código de verificación'
        ],
        'codigo_temporal': [
            r'código temporal',
            r'temporary code',
            r'one-time code',
            r'código de un solo uso'
        ],
        'actualizacion_hogar': [
            r'actualización de hogar',
            r'household update',
            r'manage your household',
            r'administra tu hogar'
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
        """Extrae el cuerpo del correo"""
        body = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    try:
                        body = part.get_payload(decode=True).decode()
                        break
                    except:
                        pass
                elif content_type == "text/html" and not body and "attachment" not in content_disposition:
                    try:
                        body = part.get_payload(decode=True).decode()
                    except:
                        pass
        else:
            try:
                body = msg.get_payload(decode=True).decode()
            except:
                pass
        
        return body
    
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
        Extrae el código o link según el tipo de correo
        
        Args:
            body: Cuerpo del correo
            email_type: Tipo de correo (codigo_inicio, codigo_temporal, actualizacion_hogar)
        
        Returns:
            El código o link encontrado, o cadena vacía
        """
        if email_type == 'codigo_inicio':
            # Para código de inicio, buscar solo códigos con contexto específico de Netflix
            # Evitar códigos de verificación genéricos
            patterns = [
                # Buscar "código para iniciar sesión" seguido del código
                r'(?:código|code).*?(?:iniciar sesión|sign-?in|login).*?(\d{4,8})',
                r'(?:iniciar sesión|sign-?in|login).*?(?:código|code).*?(\d{4,8})',
                # Buscar "Ingresa este código" seguido del código
                r'(?:ingresa|enter).*?(?:este|this).*?(?:código|code).*?(\d{4,8})',
                # Buscar el código en un contexto de inicio de sesión
                r'(?:para|to).*?(?:iniciar sesión|sign in).*?(\d{4,8})',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, body, re.IGNORECASE | re.DOTALL)
                if match:
                    return match.group(1)
            
            # Si no encuentra con contexto, buscar números de 4 dígitos exactos
            # pero solo si el correo menciona "sign-in" o "iniciar sesión"
            if re.search(r'sign-?in|iniciar sesión', body, re.IGNORECASE):
                match = re.search(r'\b(\d{4})\b', body)
                if match:
                    return match.group(1)
        
        elif email_type in ['codigo_temporal', 'actualizacion_hogar']:
            # Para código temporal y actualizar hogar, extraer el link
            patterns = [
                r'https?://[^\s<>"]+netflix\.com[^\s<>"]*',  # Links de Netflix
                r'https?://account\.netflix\.com[^\s<>"]*',
                r'https?://www\.netflix\.com[^\s<>"]*',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, body, re.IGNORECASE)
                if match:
                    # Limpiar el link de posibles caracteres HTML
                    link = match.group(0)
                    # Remover caracteres comunes al final que no son parte del link
                    link = re.sub(r'[)\]}>"\'\s]+$', '', link)
                    return link
        
        return ""
    
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
        
        # Calcular fecha de búsqueda
        search_date = (datetime.now() - timedelta(days=days_back)).strftime("%d-%b-%Y")
        
        # Buscar correos de Netflix
        status, messages = self.mail.search(None, f'(FROM "netflix.com" SINCE {search_date})')
        
        if status != "OK":
            logger.warning("No se pudieron buscar correos de Netflix")
            return []
        
        email_ids = messages[0].split()
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
                        
                        # Decodificar asunto
                        subject = self._decode_mime_words(msg["Subject"])
                        from_address = self._decode_mime_words(msg["From"])
                        date_str = msg["Date"]
                        
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
                                'date': date_str,
                                'type': email_type,
                                'code': code,
                                'body_preview': body[:200] if body else "",
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
        
        # Ordenar por fecha (más recientes primero)
        all_emails.sort(key=lambda x: x['date'], reverse=True)
        
        return all_emails

# Mantener compatibilidad con código existente
EmailMonitor = GmailMonitor
OutlookMonitor = GmailMonitor
