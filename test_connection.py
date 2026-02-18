"""
Script para probar la conexión IMAP a Outlook con las credenciales
"""
import imaplib
import json

def test_imap_connection(email, password):
    """Prueba la conexión IMAP a Outlook"""
    print(f"\n🔍 Probando conexión para: {email}")
    print("-" * 50)
    
    try:
        # Conectar al servidor IMAP de Outlook
        print("📡 Conectando a outlook.office365.com:993...")
        mail = imaplib.IMAP4_SSL("outlook.office365.com", 993)
        
        # Intentar login
        print("🔐 Intentando autenticación...")
        mail.login(email, password)
        
        print("✅ ¡CONEXIÓN EXITOSA!")
        
        # Listar carpetas disponibles
        print("\n📁 Carpetas disponibles:")
        status, folders = mail.list()
        if status == "OK":
            for folder in folders[:5]:  # Mostrar solo las primeras 5
                print(f"   - {folder.decode()}")
        
        # Seleccionar INBOX y contar correos
        print("\n📧 Verificando INBOX...")
        status, messages = mail.select("INBOX")
        if status == "OK":
            num_messages = int(messages[0])
            print(f"   ✓ {num_messages} correos en INBOX")
        
        # Buscar correos de Netflix (últimos 30 días)
        print("\n🔍 Buscando correos de Netflix...")
        status, data = mail.search(None, '(FROM "netflix.com")')
        if status == "OK":
            netflix_emails = data[0].split()
            print(f"   ✓ {len(netflix_emails)} correos de Netflix encontrados")
        
        # Cerrar conexión
        mail.close()
        mail.logout()
        
        print("\n" + "=" * 50)
        print("✅ PRUEBA EXITOSA - Las credenciales funcionan correctamente")
        print("=" * 50)
        return True
        
    except imaplib.IMAP4.error as e:
        print(f"\n❌ ERROR DE AUTENTICACIÓN: {str(e)}")
        print("\n💡 Posibles causas:")
        print("   - La contraseña no es una contraseña de aplicación")
        print("   - La contraseña es incorrecta")
        print("   - IMAP no está habilitado en la cuenta")
        print("   - La verificación en dos pasos no está activada")
        return False
        
    except Exception as e:
        print(f"\n❌ ERROR DE CONEXIÓN: {str(e)}")
        print("\n💡 Posibles causas:")
        print("   - No hay conexión a internet")
        print("   - El servidor de Outlook está caído")
        print("   - Firewall bloqueando el puerto 993")
        return False

def main():
    """Función principal"""
    print("\n" + "=" * 50)
    print("🧪 PRUEBA DE CONEXIÓN IMAP - Outlook")
    print("=" * 50)
    
    # Cargar cuentas desde accounts.json
    try:
        with open('accounts.json', 'r') as f:
            data = json.load(f)
            accounts = data.get('accounts', [])
    except FileNotFoundError:
        print("\n❌ Error: No se encontró accounts.json")
        return
    except json.JSONDecodeError:
        print("\n❌ Error: accounts.json no es un JSON válido")
        return
    
    if not accounts:
        print("\n❌ Error: No hay cuentas configuradas en accounts.json")
        return
    
    print(f"\n📊 Cuentas encontradas: {len(accounts)}")
    
    # Probar cada cuenta
    results = []
    for i, account in enumerate(accounts, 1):
        email = account.get('email')
        password = account.get('password')
        
        if not email or not password:
            print(f"\n⚠️  Cuenta {i}: Falta email o password")
            results.append(False)
            continue
        
        success = test_imap_connection(email, password)
        results.append(success)
    
    # Resumen final
    print("\n" + "=" * 50)
    print("📊 RESUMEN FINAL")
    print("=" * 50)
    
    successful = sum(results)
    total = len(results)
    
    print(f"\n✅ Exitosas: {successful}/{total}")
    print(f"❌ Fallidas: {total - successful}/{total}")
    
    if successful == total:
        print("\n🎉 ¡TODAS LAS CUENTAS ESTÁN FUNCIONANDO!")
        print("✓ Puedes hacer redeploy en Coolify con confianza")
    elif successful > 0:
        print("\n⚠️  ALGUNAS CUENTAS TIENEN PROBLEMAS")
        print("✓ Revisa las credenciales de las cuentas fallidas")
    else:
        print("\n❌ NINGUNA CUENTA FUNCIONÓ")
        print("✓ Verifica las contraseñas de aplicación")
        print("✓ Asegúrate que IMAP esté habilitado")

if __name__ == '__main__':
    main()
