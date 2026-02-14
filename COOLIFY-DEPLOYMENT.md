# 🚀 ACTUALIZACIÓN COOLIFY - Soporte Gmail + Cloudflare

## ✅ Cambios Subidos a GitHub

**Commit**: `5cb24cb`  
**Repositorio**: https://github.com/josephsmithvaz777-svg/app-netcodigo-monitor.git  
**Branch**: `main`

### Nuevas Funcionalidades:
- ✅ Soporte para Gmail (además de Outlook)
- ✅ Compatible con Cloudflare Email Routing
- ✅ Configuración multi-proveedor
- ✅ Nuevos archivos de documentación

---

## 📋 PASOS PARA ACTUALIZAR EN COOLIFY

### 1️⃣ Actualizar Variables de Entorno

Ve a tu proyecto en Coolify y **actualiza** la variable `OUTLOOK_ACCOUNTS` con solo la cuenta de Gmail:

#### ⚠️ FORMATO CORRECTO (TODO EN UNA LÍNEA):

```json
[{"email":"netflixaccglobal@gmail.com","password":"tiziijuofbuzmqop","provider":"gmail"}]
```

#### 📝 Desglosado para entender (NO uses esto, usa la línea de arriba):

```json
[
  {
    "email": "netflixaccglobal@gmail.com",
    "password": "tiziijuofbuzmqop",
    "provider": "gmail"
  }
]
```

### 2️⃣ Verificar Otras Variables de Entorno

Asegúrate de tener también:

```bash
SECRET_KEY=tu-clave-secreta-actual
PORT=5000
```

### 3️⃣ Hacer Rebuild en Coolify

1. Ve a tu proyecto en Coolify
2. Haz clic en **"Rebuild"** o **"Redeploy"**
3. Coolify descargará el nuevo código de GitHub
4. Construirá la imagen con los cambios
5. Iniciará el contenedor

### 4️⃣ Verificar el Deployment

**En los logs de Coolify deberías ver**:

```
INFO - Iniciando servidor Flask...
INFO - Cuentas cargadas desde variable de entorno: 1
INFO - Cuentas configuradas: 1
INFO - Configuración: {'check_interval': 300, 'days_back': 7, ...}
* Running on http://0.0.0.0:5000
```

**Verifica que diga "1 cuenta"** (solo Gmail)

---

## 🔍 Cómo Funciona Ahora

```
┌─────────────────────────────────────────────────────┐
│  Netflix envía código a:                            │
│  • digitalacc06@digitalstoretrujillo.store          │
│  • digitalacc08@digitalstoretrujillo.store          │
│  • Cualquier correo @digitalstoretrujillo.store     │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│  Cloudflare Email Routing (Catch-All)               │
│  Reenvía TODO a: netflixaccglobal@gmail.com         │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│  Tu App en Coolify monitorea vía IMAP:              │
│  • netflixaccglobal@gmail.com                       │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│  Interfaz web muestra TODOS los códigos             │
│  https://tu-app.coolify-url.com                     │
└─────────────────────────────────────────────────────┘
```

---

## 🔐 Seguridad

### ✅ Contraseñas Protegidas

- ✅ `accounts.json` está en `.gitignore` (NO se sube a GitHub)
- ✅ Las contraseñas están solo en variables de entorno de Coolify
- ✅ La contraseña de Gmail es una "contraseña de aplicación" (no la principal)

### 🔑 Contraseña Usada:

**Gmail** (contraseña de aplicación de Google):
- `netflixaccglobal@gmail.com`: `tiziijuofbuzmqop`

---

## 🐛 Solución de Problemas

### Si el build falla:
1. Revisa los logs en Coolify
2. Verifica que el código se haya actualizado en GitHub
3. Asegúrate que `outlook_service.py` se haya actualizado

### Si solo detecta 2 cuentas en lugar de 3:
1. Verifica que `OUTLOOK_ACCOUNTS` tenga las 3 cuentas
2. Asegúrate que el JSON sea válido (sin saltos de línea)
3. Haz rebuild después de cambiar la variable

### Si hay error con Gmail:
1. Verifica que la contraseña de aplicación sea correcta
2. Verifica que IMAP esté habilitado en Gmail
3. Regenera la contraseña de aplicación si es necesario

---

## ✅ Checklist de Deployment

- [x] Código actualizado en GitHub ✅ (commit `5cb24cb`)
- [ ] Variable `OUTLOOK_ACCOUNTS` actualizada en Coolify con Gmail
- [ ] Rebuild ejecutado en Coolify
- [ ] Logs muestran "1 cuenta configurada"
- [ ] Aplicación accesible en la URL de Coolify
- [ ] Prueba de verificación manual funciona
- [ ] Correos de Gmail se muestran correctamente

---

## 🎯 Resultado Esperado

Después del deployment, tu aplicación en Coolify:

1. ✅ Monitoreará **1 cuenta** (Gmail)
2. ✅ Detectará correos de Netflix de **netflixaccglobal@gmail.com**
3. ✅ Mostrará códigos que lleguen a `@digitalstoretrujillo.store`
4. ✅ Actualizará automáticamente cada 5 minutos
5. ✅ Permitirá verificación manual instantánea

---

## 📚 Documentación Adicional

Archivos nuevos en el repositorio:
- **`LEER-PRIMERO.md`** - Resumen ejecutivo
- **`INICIO-RAPIDO.md`** - Guía paso a paso
- **`CONFIGURACION-GMAIL.md`** - Guía detallada de Gmail
- **`CAMBIOS-MULTI-PROVEEDOR.md`** - Documentación técnica
- **`test_gmail.py`** - Script de prueba

---

## 🚀 ¡Listo para Deployment!

**Próximos pasos**:
1. Copia la variable `OUTLOOK_ACCOUNTS` de arriba
2. Pégala en Coolify (reemplaza la anterior)
3. Haz Rebuild
4. ¡Disfruta! 🎉

---

**Última actualización**: 2026-02-13  
**Commit**: `5cb24cb`
