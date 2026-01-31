# 🚀 Guía de Deployment en Coolyfi

## 📦 Preparación del Proyecto

Tu proyecto ya está listo para ser desplegado en Coolyfi con Docker.

## 🔧 Configuración de Variables de Entorno

Antes de desplegar, necesitas configurar las siguientes variables de entorno en Coolyfi:

### Variables Requeridas:

1. **OUTLOOK_ACCOUNTS** (JSON string):
```json
[{"email":"cuenta1@outlook.com","password":"contraseña-app"},{"email":"cuenta2@outlook.com","password":"contraseña-app"}]
```

2. **SECRET_KEY**:
```
genera-una-clave-secreta-aleatoria-aqui
```

3. **PORT** (opcional, por defecto 5000):
```
5000
```

### Variables Opcionales:

- **DEBUG**: `False` (para producción)

## 📝 Pasos para Deployment en Coolyfi

### 1. Conectar tu Repositorio Git

```bash
# Si aún no tienes un repositorio Git
git init
git add .
git commit -m "Initial commit - Netflix Codes Monitor"

# Conectar a tu repositorio remoto (GitHub, GitLab, etc.)
git remote add origin https://github.com/tu-usuario/app-codigos-netflix.git
git push -u origin main
```

### 2. Crear Proyecto en Coolyfi

1. Ve a https://coolyfi.com (o tu panel de Coolyfi)
2. Haz clic en "New Project" o "Nuevo Proyecto"
3. Selecciona "Deploy from Git Repository"
4. Conecta tu repositorio

### 3. Configurar el Deployment

En Coolyfi, configura:

- **Build Method**: Docker
- **Dockerfile Path**: `./Dockerfile`
- **Port**: `5000`

### 4. Configurar Variables de Entorno

En el panel de Coolyfi, añade las variables de entorno:

**Método 1: Usando JSON en variable de entorno** (Recomendado para Coolyfi)

```
Variable: OUTLOOK_ACCOUNTS
Valor: [{"email":"cuenta1@outlook.com","password":"password1"},{"email":"cuenta2@outlook.com","password":"password2"}]

Variable: SECRET_KEY
Valor: tu-clave-secreta-super-aleatoria-12345

Variable: PORT
Valor: 5000
```

**Método 2: Usando archivo accounts.json** (Alternativo)

Si Coolyfi permite subir archivos de configuración:
1. Crea un archivo `accounts.json` con tus cuentas
2. Súbelo a Coolyfi como archivo de configuración
3. Asegúrate que esté en el directorio `/app/`

### 5. Deploy

Haz clic en "Deploy" y espera a que se construya la imagen Docker.

## 🔒 Seguridad en Producción

### Generar una clave secreta segura

Puedes usar Python para generar una clave aleatoria:

```python
import secrets
print(secrets.token_hex(32))
```

O en PowerShell:
```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

Copia el resultado y úsalo como `SECRET_KEY`.

### Proteger tus contraseñas

- ✅ Usa siempre **contraseñas de aplicación** de Microsoft, nunca tu contraseña real
- ✅ **NO** incluyas `accounts.json` en el repositorio Git (ya está en `.gitignore`)
- ✅ Usa las variables de entorno de Coolyfi para almacenar credenciales
- ✅ Rota las contraseñas de aplicación periódicamente

## 🌐 Acceder a tu Aplicación

Una vez desplegada, Coolyfi te dará una URL como:

```
https://tu-app.coolyfi.app
```

O puedes configurar un dominio personalizado:

```
https://netflix-monitor.tudominio.com
```

## 📊 Monitoreo y Logs

### Ver Logs en Coolyfi

1. Ve a tu proyecto en Coolyfi
2. Haz clic en "Logs" o "Registros"
3. Verás los logs de la aplicación Flask

### Comandos útiles para debuggear

Si Coolyfi permite acceso a la terminal:

```bash
# Ver logs en tiempo real
docker logs -f <container-id>

# Ver archivos de configuración
cat /app/accounts.json
cat /app/settings.json

# Verificar conexión IMAP
python -c "import imaplib; m = imaplib.IMAP4_SSL('outlook.office365.com', 993); print('OK')"
```

## ⚡ Optimización para Producción

### 1. Ajustar el intervalo de verificación

En `settings.json` o como variable de entorno:

```json
{
  "check_interval": 300,  // 5 minutos (recomendado para producción)
  "days_back": 7,
  "auto_mark_read": false,
  "notification_enabled": true
}
```

### 2. Limitar el número de cuentas

Para evitar bloqueos de Microsoft:
- Máximo 5-10 cuentas por instancia
- Si necesitas más, considera múltiples instancias

### 3. Configurar Health Checks

Si Coolyfi lo soporta, añade un health check:

```
Endpoint: /api/stats
Método: GET
Expected Status: 200
Interval: 60s
```

## 🔄 Actualizar la Aplicación

Para actualizar tu deployment:

```bash
# Hacer cambios en tu código
git add .
git commit -m "Actualización: descripción de cambios"
git push

# Coolyfi detectará el push y re-desplegará automáticamente
```

## 🐛 Solución de Problemas en Producción

### Error: "Cannot connect to IMAP"

- Verifica que las credenciales en `OUTLOOK_ACCOUNTS` sean correctas
- Asegúrate de usar contraseñas de aplicación
- Verifica que el contenedor tenga acceso a internet

### Error: "Port already in use"

- Verifica que el `PORT` en Coolyfi sea 5000 o el puerto configurado
- Asegúrate que no haya conflictos con otros servicios

### La aplicación se reinicia constantemente

- Revisa los logs para ver el error específico
- Verifica que `accounts.json` esté bien formado (JSON válido)
- Asegúrate que las dependencias se instalaron correctamente

## 📞 Soporte

Si tienes problemas específicos con Coolyfi, consulta:
- Documentación de Coolyfi
- Support de Coolyfi
- Community forums

## 🎉 ¡Listo!

Tu aplicación Netflix Codes Monitor ya está en producción en Coolyfi.

Accede a ella desde cualquier dispositivo y monitorea tus códigos de Netflix en tiempo real.

---

**Deployment creado con ❤️ para Coolyfi**
