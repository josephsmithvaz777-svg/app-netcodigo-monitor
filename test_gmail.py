"""
Script de prueba para verificar la conexión IMAP a Gmail
"""
import sys
from outlook_service import IMAPService
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_gmail_connection():
    """Prueba la conexión a Gmail"""
    
    print("=" * 60)
    print("🧪 TEST DE CONEXIÓN GMAIL")
    print("=" * 60)
    
    # Solicitar credenciales
    email = input("\n📧 Ingresa tu correo de Gmail: ").strip()
    password = input("🔑 Ingresa tu contraseña de aplicación: ").strip()
    
    print("\n🔄 Intentando conectar a Gmail...")
    
    try:
        # Crear servicio IMAP
        service = IMAPService(
            email_address=email,
            password=password,
            provider='gmail'
        )
        
        # Intentar conectar
        service.connect()
        print("✅ ¡Conexión exitosa!")
        
        # Buscar correos de Netflix
        print("\n🔍 Buscando correos de Netflix (últimos 7 días)...")
        emails = service.fetch_netflix_emails(days_back=7)
        
        print(f"\n📊 Resultados:")
        print(f"   Total de correos de Netflix encontrados: {len(emails)}")
        
        if emails:
            print("\n📧 Últimos correos encontrados:")
            for i, email_data in enumerate(emails[:5], 1):
                print(f"\n   {i}. {email_data['subject']}")
                print(f"      Tipo: {email_data['type']}")
                print(f"      Fecha: {email_data['date']}")
                print(f"      Cuenta: {email_data['account']}")
                if email_data.get('code'):
                    print(f"      Código: {email_data['code']}")
        else:
            print("\n⚠️  No se encontraron correos de Netflix en los últimos 7 días")
            print("   Esto puede ser normal si no has recibido correos de Netflix recientemente")
        
        # Desconectar
        service.disconnect()
        print("\n✅ Test completado exitosamente")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\n💡 Posibles soluciones:")
        print("   1. Verifica que la contraseña de aplicación sea correcta")
        print("   2. Asegúrate de tener IMAP habilitado en Gmail")
        print("   3. Verifica que la verificación en dos pasos esté activa")
        print("   4. Genera una nueva contraseña de aplicación")
        print("\n📖 Ver guía: CONFIGURACION-GMAIL.md")
        return False

if __name__ == "__main__":
    success = test_gmail_connection()
    sys.exit(0 if success else 1)
