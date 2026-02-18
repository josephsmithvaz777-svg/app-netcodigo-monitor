"""
Script de diagnóstico avanzado para IMAP Outlook
"""
import imaplib
import json
import ssl

def test_outlook_detailed(email, password):
    """Prueba detallada de conexión a Outlook"""
    print(f"\n{'='*60}")
    print(f"🔍 Diagnóstico detallado para: {email}")
    print('='*60)
    
    # Probar diferentes métodos de autenticación
    methods = [
        ("IMAP SSL Estándar", "outlook.office365.com", 993),
        ("IMAP SSL Alternativo", "imap-mail.outlook.com", 993),
    ]
    
    for method_name, server, port in methods:
        print(f"\n📡 Intentando: {method_name}")
        print(f"   Servidor: {server}:{port}")
        
        try:
            # Crear contexto SSL
            context = ssl.create_default_context()
            
            # Conectar
            mail = imaplib.IMAP4_SSL(server, port, ssl_context=context)
            print(f"   ✓ Conexión SSL establecida")
            
            # Verificar capacidades
            capabilities = mail.capabilities
            print(f"   ✓ Capacidades: {capabilities}")
            
            # Intentar login
            try:
                result = mail.login(email, password)
                print(f"   ✅ LOGIN EXITOSO: {result}")
                
                # Listar carpetas
                status, folders = mail.list()
                print(f"\n   📁 Carpetas disponibles:")
                for folder in folders[:3]:
                    print(f"      - {folder.decode()}")
                
                mail.logout()
                return True
                
            except imaplib.IMAP4.error as e:
                error_msg = str(e)
                print(f"   ❌ Error de autenticación: {error_msg}")
                
                # Diagnóstico específico
                if b'LOGIN failed' in str(e).encode() or 'LOGIN failed' in str(e):
                    print(f"\n   💡 Diagnóstico:")
                    print(f"      - Las credenciales fueron rechazadas")
                    print(f"      - Verifica que la contraseña sea exacta")
                    print(f"      - Asegúrate que no tenga espacios al inicio/final")
                
                if b'AUTHENTICATE' in str(e).encode():
                    print(f"      - El servidor requiere OAuth2")
                    print(f"      - Las contraseñas de aplicación pueden no estar permitidas")
                
                mail.logout()
                
        except Exception as e:
            print(f"   ❌ Error de conexión: {type(e).__name__}: {str(e)}")
    
    return False

def main():
    print("\n" + "="*60)
    print("🔬 DIAGNÓSTICO AVANZADO - IMAP OUTLOOK")
    print("="*60)
    
    # Cargar cuentas
    try:
        with open('accounts.json', 'r') as f:
            data = json.load(f)
            accounts = data.get('accounts', [])
    except Exception as e:
        print(f"\n❌ Error cargando accounts.json: {e}")
        return
    
    if not accounts:
        print("\n❌ No hay cuentas configuradas")
        return
    
    print(f"\n📊 Cuentas a probar: {len(accounts)}")
    
    results = []
    for account in accounts:
        email = account.get('email', '')
        password = account.get('password', '')
        
        if not email or not password:
            print(f"\n⚠️  Cuenta sin email o password")
            continue
        
        # Verificar que no tenga espacios
        if password != password.strip():
            print(f"\n⚠️  ADVERTENCIA: La contraseña tiene espacios al inicio o final")
            password = password.strip()
            print(f"   Contraseña limpia: '{password}'")
        
        print(f"\n📧 Email: {email}")
        print(f"🔑 Password length: {len(password)} caracteres")
        print(f"🔑 Password: {password[:4]}...{password[-4:]} (parcial)")
        
        success = test_outlook_detailed(email, password)
        results.append(success)
    
    # Resumen
    print("\n" + "="*60)
    print("📊 RESUMEN")
    print("="*60)
    
    successful = sum(results)
    total = len(results)
    
    print(f"\n✅ Exitosas: {successful}/{total}")
    print(f"❌ Fallidas: {total - successful}/{total}")
    
    if successful == 0:
        print("\n💡 RECOMENDACIONES:")
        print("   1. Verifica que copiaste las contraseñas exactamente")
        print("   2. Espera 5-10 minutos y vuelve a intentar")
        print("   3. Revoca las contraseñas viejas en Microsoft")
        print("   4. Genera nuevas contraseñas de aplicación")
        print("   5. Si sigue fallando, necesitaremos implementar OAuth2")

if __name__ == '__main__':
    main()
