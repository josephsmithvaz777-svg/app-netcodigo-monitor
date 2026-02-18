# ✅ CÓDIGO SUBIDO A GITHUB - LISTO PARA COOLIFY

## 🎉 ¡Push Exitoso!

Tu código Python se ha subido correctamente a:
**https://github.com/josephsmithvaz777-svg/app-netcodigo-monitor.git**

## 🚀 Próximos Pasos para Coolify

### 1️⃣ Configurar Variables de Entorno en Coolify

Ve a tu proyecto en Coolify y configura estas variables de entorno:

#### Variables Requeridas:

```bash
OUTLOOK_ACCOUNTS=[{"email":"cuenta1@outlook.com","password":"tu-contraseña-app"},{"email":"cuenta2@outlook.com","password":"tu-contraseña-app"}]

SECRET_KEY=genera-una-clave-aleatoria-aqui

PORT=5000
```

**Para generar SECRET_KEY:**
```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

#### Formato Correcto de OUTLOOK_ACCOUNTS:

⚠️ **IMPORTANTE**: Todo en UNA SOLA LÍNEA, sin saltos de línea:

```json
[{"email":"cuenta1@outlook.com","password":"xxxx"},{"email":"cuenta2@outlook.com","password":"yyyy"}]
```

### 2️⃣ Verificar Configuración de Build en Coolify

En Coolify, asegúrate que esté configurado:

- **Repository**: `https://github.com/josephsmithvaz777-svg/app-netcodigo-monitor.git`
- **Branch**: `main`
- **Build Method**: `Dockerfile`
- **Dockerfile Location**: `./Dockerfile`
- **Port**: `5000`

### 3️⃣ Hacer Rebuild en Coolify

1. Ve a tu proyecto en Coolify
2. Haz clic en **"Rebuild"** o **"Redeploy"**
3. Coolify detectará el nuevo código (Python)
4. Construirá la imagen usando el Dockerfile
5. Iniciará el contenedor

### 4️⃣ Verificar el Deployment

**Espera a que termine el build** (puede tomar 2-3 minutos).

**Revisa los logs en Coolify**, deberías ver:
```
INFO - Iniciando servidor Flask...
INFO - Cuentas cargadas desde variable de entorno: X
INFO - Cuentas configuradas: X
```

**Accede a tu aplicación**:
```
https://tu-app.coolify-url.com/
```

## 🔑 IMPORTANTE: Contraseñas de Aplicación

⚠️ **NO uses tus contraseñas normales de Outlook**. Debes usar **contraseñas de aplicación**:

### Cómo generar contraseñas de aplicación:

1. Ve a: **https://account.microsoft.com/security**
2. Haz clic en **"Opciones de seguridad avanzadas"**
3. Activa **"Verificación en dos pasos"** (si no está activa)
4. Ve a **"Contraseñas de aplicación"**
5. Haz clic en **"Crear una nueva contraseña de aplicación"**
6. Se generará un código como: `abcd efgh ijkl mnop`
7. **Copia este código (sin espacios)**: `abcdefghijklmnop`
8. Úsalo en `OUTLOOK_ACCOUNTS`

### Verificar que IMAP esté habilitado:

1. Ve a: **https://outlook.live.com/mail/**
2. Configuración (⚙️) > **"Ver toda la configuración"**
3. **"Correo"** > **"Sincronizar correo"**
4. Asegúrate que **"Permitir que dispositivos usen IMAP"** esté **activado**

## 📊 Ejemplo Completo de Variables de Entorno

```bash
# Nombre: OUTLOOK_ACCOUNTS
# Valor (ejemplo con 3 cuentas):
[{"email":"netflix1@outlook.com","password":"abcdefgh1234"},{"email":"netflix2@outlook.com","password":"ijklmnop5678"},{"email":"netflix3@outlook.com","password":"qrstuvwx9012"}]

# Nombre: SECRET_KEY
# Valor (genera uno aleatorio):
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2

# Nombre: PORT
# Valor:
5000
```

## 🐛 Solución Rápida de Problemas

### Si el build falla:

1. **Revisa los logs en Coolify**
2. Verifica que el Dockerfile existe en el repo
3. Asegúrate que `requirements.txt` existe

### Si la app arranca pero no hay cuentas:

1. **Verifica `OUTLOOK_ACCOUNTS` en Coolify**
2. Asegúrate que el JSON sea válido (usa un validador JSON online)
3. Rebuild después de cambiar variables de entorno

### Si hay error de autenticación:

1. **Verifica que uses contraseñas de aplicación**, no contraseñas normales
2. Regenera las contraseñas de aplicación en Microsoft
3. Actualiza `OUTLOOK_ACCOUNTS`
4. Rebuild

## ✅ Checklist Pre-Deployment

- [x] Código subido a GitHub ✅
- [ ] Variables de entorno configuradas en Coolify
  - [ ] `OUTLOOK_ACCOUNTS` con contraseñas de aplicación
  - [ ] `SECRET_KEY` generada
  - [ ] `PORT=5000`
- [ ] Contraseñas de aplicación generadas en Microsoft
- [ ] IMAP habilitado en cuentas Outlook
- [ ] Rebuild ejecutado en Coolify

## 🎯 Qué Esperar

Después del deployment:

1. **Interfaz web moderna** estilo Netflix en tu URL de Coolify
2. **Dashboard con estadísticas** de correos de Netflix
3. **Monitoreo en tiempo real** con actualizaciones automáticas
4. **Filtros** por tipo de correo y cuenta
5. **Copia rápida** de códigos de verificación

## 📖 Documentación Adicional

- **`DEPLOYMENT.md`** - Guía completa de deployment
- **`README.md`** - Documentación técnica
- **`INICIO-RAPIDO.md`** - Guía de uso rápido
- **`RESUMEN.md`** - Resumen del proyecto

## 🎉 ¡Listo!

Tu aplicación está lista para deployment en Coolify. Solo necesitas:

1. **Configurar las variables de entorno** en Coolify
2. **Hacer Rebuild**
3. **¡Disfrutar!** 🚀

---

**Commit subido**: ✅ `da1b507`  
**Repositorio**: https://github.com/josephsmithvaz777-svg/app-netcodigo-monitor.git  
**Branch**: `main`
