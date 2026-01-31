#!/usr/bin/env python
"""
Script de prueba para verificar la configuración antes de deployment
"""

import json
import os
import sys

def check_file(filepath, description):
    """Verifica si un archivo existe"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} NO encontrado: {filepath}")
        return False

def check_json_file(filepath, description):
    """Verifica si un archivo JSON es válido"""
    if not check_file(filepath, description):
        return False
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"   └─ JSON válido ✓")
        return True
    except json.JSONDecodeError as e:
        print(f"   └─ ERROR: JSON inválido - {str(e)}")
        return False

def check_accounts():
    """Verifica la configuración de cuentas"""
    print("\n📧 Verificando cuentas...")
    
    # Primero verificar variable de entorno
    env_accounts = os.environ.get('OUTLOOK_ACCOUNTS')
    if env_accounts:
        print("✅ Variable de entorno OUTLOOK_ACCOUNTS encontrada")
        try:
            accounts = json.loads(env_accounts)
            print(f"   └─ {len(accounts)} cuenta(s) configurada(s)")
            for i, acc in enumerate(accounts, 1):
                email = acc.get('email', 'NO EMAIL')
                has_pass = 'password' in acc and acc['password']
                status = "✓" if has_pass else "✗"
                print(f"      {i}. {email} [{status}]")
            return True
        except json.JSONDecodeError as e:
            print(f"❌ Error al parsear JSON: {str(e)}")
            return False
    
    # Si no hay variable de entorno, verificar archivo
    if check_json_file('accounts.json', 'Archivo de cuentas'):
        with open('accounts.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        accounts = data.get('accounts', [])
        if len(accounts) == 0:
            print("⚠️  ADVERTENCIA: No hay cuentas configuradas en accounts.json")
            return False
        
        print(f"   └─ {len(accounts)} cuenta(s) configurada(s)")
        for i, acc in enumerate(accounts, 1):
            email = acc.get('email', 'NO EMAIL')
            has_pass = 'password' in acc and acc['password']
            status = "✓" if has_pass else "✗"
            print(f"      {i}. {email} [{status}]")
        return True
    
    return False

def check_dependencies():
    """Verifica las dependencias de Python"""
    print("\n📦 Verificando dependencias de Python...")
    
    required_modules = [
        'flask',
        'flask_socketio',
        'imapclient',
        'bs4'
    ]
    
    all_installed = True
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} - NO INSTALADO")
            all_installed = False
    
    return all_installed

def check_settings():
    """Verifica la configuración"""
    print("\n⚙️  Verificando configuración...")
    
    if check_json_file('settings.json', 'Archivo de configuración'):
        with open('settings.json', 'r', encoding='utf-8') as f:
            settings = json.load(f)
        
        interval = settings.get('check_interval', 300)
        days = settings.get('days_back', 7)
        
        print(f"   └─ Intervalo de verificación: {interval} segundos")
        if interval < 60:
            print("      ⚠️  ADVERTENCIA: Intervalo muy bajo, riesgo de bloqueo")
        
        print(f"   └─ Días hacia atrás: {days}")
        if days > 30:
            print("      ⚠️  ADVERTENCIA: Demasiados días, puede ser lento")
        
        return True
    return False

def check_docker():
    """Verifica archivos Docker"""
    print("\n🐳 Verificando archivos Docker...")
    
    dockerfile_ok = check_file('Dockerfile', 'Dockerfile')
    dockerignore_ok = check_file('.dockerignore', 'Docker ignore')
    
    return dockerfile_ok and dockerignore_ok

def main():
    """Función principal"""
    print("=" * 60)
    print("🔍 VERIFICACIÓN PRE-DEPLOYMENT - Netflix Codes Monitor")
    print("=" * 60)
    
    checks = []
    
    # Verificar archivos principales
    print("\n📁 Verificando archivos principales...")
    checks.append(check_file('app.py', 'Aplicación principal'))
    checks.append(check_file('outlook_service.py', 'Servicio IMAP'))
    checks.append(check_file('requirements.txt', 'Dependencias'))
    
    # Verificar configuración
    checks.append(check_accounts())
    checks.append(check_settings())
    
    # Verificar dependencias
    checks.append(check_dependencies())
    
    # Verificar Docker
    checks.append(check_docker())
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN")
    print("=" * 60)
    
    total_checks = len(checks)
    passed_checks = sum(checks)
    
    print(f"Verificaciones completadas: {passed_checks}/{total_checks}")
    
    if passed_checks == total_checks:
        print("\n✅ ¡TODO LISTO PARA DEPLOYMENT!")
        print("\nPróximos pasos:")
        print("1. Ejecuta 'python app.py' para probar localmente")
        print("2. Si funciona, sube a Git y deploya en Coolyfi")
        print("3. Configura las variables de entorno en Coolyfi")
        return 0
    else:
        print("\n❌ HAY PROBLEMAS QUE DEBEN SER CORREGIDOS")
        print("\nRevisa los errores arriba y corrígelos antes de deployment")
        return 1

if __name__ == '__main__':
    sys.exit(main())
