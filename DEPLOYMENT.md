# 🚀 Guía de Deployment en Coolify

## ✅ Commit Listo

Tu código ya está en commit y listo para ser subido a GitHub.

## 📤 Paso 1: Push a GitHub

Cuando tengas conexión estable a internet, ejecuta:

```bash
git push origin main
```

Si el push falla por problemas de conexión, intenta:

```bash
# Verificar conexión
ping github.com

# Reintentar push
git push origin main

# Si sigue fallando, usa SSH en lugar de HTTPS
git remote set-url origin git@github.com:josephsmithvaz777-svg/app-netcodigo-monitor.git
git push origin main
```

## 🐳 Paso 2: Configurar en Coolify

### A. Acceder a Coolify

1. Ve a tu panel de Coolify
2. Busca el proyecto: **app-netcodigo-monitor**
3. Haz clic en el proyecto

### B. Verificar Configuración de Build

Actualiza la configuración del proyecto en Coolify:

**Build Configuration:**
- **Build Method**: `Dockerfile`
- **Dockerfile Location**: `./Dockerfile`
- **Build Context**: `.` (raíz del proyecto)
- **Port**: `5000`

### C. Configurar Variables de Entorno

En Coolify, ve a **Environment Variables** y añade:

#### Variables Requeridas:

```bash
# Cuentas de Outlook (JSON)
OUTLOOK_ACCOUNTS=[{"email":"cuenta1@outlook.com","password":"contraseña-app1"},{"email":"cuenta2@outlook.com","password":"contraseña-app2"}]

# Clave secreta (genera una aleatoria)
SECRET_KEY=tu-clave-secreta-super-aleatoria-aqui

# Puerto (debe ser 5000)
PORT=5000
```

#### Variables Opcionales:

```bash
# Debug mode (False para producción)
DEBUG=False

# Python unbuffered (recomendado para logs)
PYTHONUNBUFFERED=1
```

### D. Generar Clave Secreta

Para generar una clave secreta aleatoria segura, usa:

**En Windows PowerShell:**
```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

Copia el resultado y úsalo como `SECRET_KEY`.

### E. Formato de OUTLOOK_ACCOUNTS

**Importante**: El valor debe ser un JSON válido en UNA SOLA LÍNEA:

```json
[{"email":"cuenta1@outlook.com","password":"xxxx"},{"email":"cuenta2@outlook.com","password":"yyyy"}]
```

**NO uses**:
- ❌ Saltos de línea
- ❌ Espacios extras
- ❌ Comillas simples en el JSON (usa comillas dobles)

**Ejemplo con múltiples cuentas:**
```json
[{"email":"cuenta1@outlook.com","password":"abcd1234"},{"email":"cuenta2@outlook.com","password":"efgh5678"},{"email":"cuenta3@outlook.com","password":"ijkl9012"}]
```

## 🔄 Paso 3: Rebuild en Coolify

Una vez configuradas las variables de entorno:

1. En Coolify, ve a tu proyecto
2. Haz clic en **"Rebuild"** o **"Redeploy"**
3. Coolify detectará el nuevo código de GitHub
4. Construirá la imagen Docker usando el `Dockerfile`
5. Iniciará el contenedor

### Logs de Build

Mientras se construye, revisa los logs en Coolify para ver:
- ✅ Instalación de dependencias Python
- ✅ Carga de cuentas desde variable de entorno
- ✅ Inicio del servidor Flask
- ✅ Puerto 5000 expuesto

## 🌐 Paso 4: Acceder a la Aplicación

Una vez deployado, Coolify te dará una URL como:

```
https://app-netcodigo-monitor.tu-dominio.com
```

O la URL que hayas configurado en Coolify.

## 🔍 Verificación Post-Deployment

### A. Verificar que la app está corriendo

```bash
# En Coolify, ve a "Logs" y deberías ver:
INFO - Iniciando servidor Flask...
INFO - Cuentas cargadas desde variable de entorno: X
INFO - Configuración: {...}
```

### B. Probar la API

Accede a estas URLs para verificar:

```
https://tu-app.com/                # Interfaz web
https://tu-app.com/api/stats       # Estadísticas
https://tu-app.com/api/accounts    # Lista de cuentas (sin contraseñas)
```

### C. Probar el monitoreo

1. Abre la interfaz web
2. Haz clic en **"Verificar Ahora"**
3. Deberías ver correos de Netflix (si hay)
4. Haz clic en **"Iniciar Monitoreo"** para monitoreo automático

## 🐛 Solución de Problemas en Coolify

### Error: "No hay cuentas configuradas"

**Causa**: Variable de entorno `OUTLOOK_ACCOUNTS` no configurada o mal formateada.

**Solución**:
1. Ve a Environment Variables en Coolify
2. Verifica que `OUTLOOK_ACCOUNTS` esté bien escrito
3. Verifica que el JSON sea válido (sin saltos de línea)
4. Rebuild

### Error: "Authentication failed"

**Causa**: Contraseñas incorrectas o no son contraseñas de aplicación.

**Solución**:
1. Verifica que uses **contraseñas de aplicación** de Microsoft
2. Genera nuevas contraseñas en: https://account.microsoft.com/security
3. Actualiza `OUTLOOK_ACCOUNTS` en Coolify
4. Rebuild

### Error: "Port 5000 already in use"

**Causa**: Configuración incorrecta del puerto.

**Solución**:
1. Verifica que `PORT=5000` en las variables de entorno
2. En Coolify, verifica que el "Port" esté configurado como `5000`
3. Rebuild

### La aplicación se reinicia constantemente

**Causa**: Error en el código o dependencias no instaladas.

**Solución**:
1. Revisa los logs en Coolify para ver el error específico
2. Verifica que todas las dependencias se instalaron (`requirements.txt`)
3. Si ves errores de IMAP, verifica las credenciales

### No se muestran correos

**Causa**: Varias posibilidades.

**Solución**:
1. Verifica que haya correos de Netflix en las cuentas
2. Verifica que sean correos recientes (últimos 7 días por defecto)
3. Revisa los logs para ver si hay errores de conexión IMAP
4. Verifica que las cuentas tengan IMAP habilitado en Outlook

## 📊 Monitoreo en Producción

### Health Check

Configura un health check en Coolify:
- **Endpoint**: `/api/stats`
- **Method**: `GET`
- **Expected Status**: `200`
- **Interval**: `60s`

### Logs

Para ver logs en tiempo real en Coolify:
1. Ve a tu proyecto
2. Haz clic en **"Logs"**
3. Activa "Auto-scroll" para ver logs en vivo

### Recursos

Monitorea el uso de recursos:
- **CPU**: Debería ser bajo (~5-10% en idle)
- **RAM**: ~200-500 MB dependiendo de las cuentas
- **Network**: Picos cada X segundos (según intervalo)

## 🔒 Seguridad en Producción

### 1. Contraseñas de Aplicación

✅ **SIEMPRE** usa contraseñas de aplicación de Microsoft
❌ **NUNCA** uses tus contraseñas reales de Outlook

### 2. Variables de Entorno

Las variables de entorno en Coolify son seguras:
- ✅ Encriptadas en tránsito
- ✅ No visibles en logs
- ✅ No se guardan en el código

### 3. HTTPS

Asegúrate que Coolify esté configurado con HTTPS:
- Coolify maneja esto automáticamente con Let's Encrypt
- Verifica que la URL use `https://`

## 🔄 Actualizar la Aplicación

Para actualizar después del deployment inicial:

```bash
# 1. Hacer cambios en tu código local
# 2. Commit
git add .
git commit -m "Descripción de cambios"

# 3. Push
git push origin main

# 4. En Coolify, hacer rebuild
# (Coolify puede detectar el push automáticamente si está configurado)
```

## 📈 Optimización para Producción

### 1. Ajustar Intervalo de Monitoreo

Para producción, usa intervalos más largos:

```bash
# Configurar en Coolify como variable de entorno (opcional)
CHECK_INTERVAL=300  # 5 minutos
DAYS_BACK=7
```

O edita `settings.json` en el repositorio antes de hacer push.

### 2. Limitar Cuentas

Para mejor rendimiento:
- Máximo 10 cuentas por instancia
- Si necesitas más, considera múltiples instancias de Coolify

### 3. Escalar

Si tienes muchas cuentas, considera:
- Usar Coolify con múltiples workers
- Aumentar recursos (CPU/RAM) en Coolify
- Distribuir cuentas en múltiples deployments

## 🎉 Checklist de Deployment

Antes de hacer rebuild en Coolify, verifica:

- [ ] Código subido a GitHub (`git push origin main`)
- [ ] Variable `OUTLOOK_ACCOUNTS` configurada en Coolify
- [ ] Variable `SECRET_KEY` configurada en Coolify
- [ ] Variable `PORT=5000` configurada en Coolify
- [ ] Dockerfile presente en el repositorio
- [ ] requirements.txt presente
- [ ] Contraseñas de aplicación generadas en Microsoft
- [ ] IMAP habilitado en cuentas de Outlook

Una vez todo esté ✅, haz **Rebuild** en Coolify.

## 📞 Soporte

Si tienes problemas:
1. Revisa los logs en Coolify
2. Verifica las variables de entorno
3. Consulta `README.md` para más detalles técnicos
4. Revisa `RESUMEN.md` para guía general

---

**¡Listo para producción en Coolify! 🚀**
