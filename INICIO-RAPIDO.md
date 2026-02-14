# ✅ PASOS RÁPIDOS - Configuración Gmail para Netflix Monitor

## 🎯 Resumen
Tu configuración actual:
- ✅ Cloudflare Email Routing configurado
- ✅ `digitalacc06@digitalstoretrujillo.store` → `netflixaccglobal@gmail.com`
- ✅ `digitalacc08@digitalstoretrujillo.store` → `netflixaccglobal@gmail.com`
- ✅ Código actualizado para soportar Gmail
- ⏳ **FALTA**: Configurar contraseña de aplicación de Gmail

---

## 📋 Checklist de Configuración

### Paso 1: Generar Contraseña de Aplicación de Gmail ⏱️ 2 minutos

1. **Abre**: https://myaccount.google.com/apppasswords
   
2. **Si no puedes acceder**, primero activa la verificación en dos pasos:
   - Ve a: https://myaccount.google.com/security
   - Busca "Verificación en dos pasos" y actívala
   - Luego vuelve a: https://myaccount.google.com/apppasswords

3. **Genera la contraseña**:
   - Selecciona app: "Correo" o "Otra (nombre personalizado)" → escribe: `Netflix Monitor`
   - Selecciona dispositivo: "Otro" → escribe: `Python IMAP`
   - Clic en "Generar"

4. **Copia la contraseña** (16 caracteres, sin espacios)
   - Ejemplo: `abcd efgh ijkl mnop` → copiar como: `abcdefghijklmnop`

### Paso 2: Habilitar IMAP en Gmail ⏱️ 1 minuto

1. **Abre Gmail**: https://mail.google.com
2. **Configuración** (⚙️) → "Ver toda la configuración"
3. **Pestaña**: "Reenvío y correo POP/IMAP"
4. **Habilitar IMAP** → "Guardar cambios"

### Paso 3: Actualizar accounts.json ⏱️ 30 segundos

Abre `accounts.json` y reemplaza `TU_CONTRASEÑA_DE_APLICACION_GMAIL_AQUI` con la contraseña generada:

```json
{
    "accounts": [
        {
            "email": "digitalstoretrujillo05@outlook.com",
            "password": "jqpbwmiapmkrynhm",
            "provider": "outlook"
        },
        {
            "email": "digitalstoretrujillo03@outlook.com",
            "password": "nbddjiyvidcsmrdp",
            "provider": "outlook"
        },
        {
            "email": "netflixaccglobal@gmail.com",
            "password": "PEGA_AQUI_LA_CONTRASEÑA_DE_16_CARACTERES",
            "provider": "gmail"
        }
    ]
}
```

### Paso 4: Probar la Conexión ⏱️ 1 minuto

```bash
python test_gmail.py
```

Ingresa cuando te pida:
- Email: `netflixaccglobal@gmail.com`
- Contraseña: `la contraseña de 16 caracteres que generaste`

**Resultado esperado**:
```
✅ ¡Conexión exitosa!
🔍 Buscando correos de Netflix...
📊 Total de correos de Netflix encontrados: X
```

### Paso 5: Ejecutar la Aplicación ⏱️ 30 segundos

```bash
python app.py
```

Abre en el navegador: http://localhost:5000

---

## 🎉 ¡Listo!

Una vez completados estos pasos, la aplicación monitoreará:
- ✅ `digitalstoretrujillo05@outlook.com`
- ✅ `digitalstoretrujillo03@outlook.com`
- ✅ `netflixaccglobal@gmail.com` (que recibe correos de Cloudflare)

Los correos de Netflix que lleguen a:
- `digitalacc06@digitalstoretrujillo.store`
- `digitalacc08@digitalstoretrujillo.store`

Serán reenviados por Cloudflare a `netflixaccglobal@gmail.com` y la aplicación los detectará automáticamente.

---

## ❓ Problemas Comunes

### "No puedo acceder a contraseñas de aplicación"
→ Activa primero la verificación en dos pasos en: https://myaccount.google.com/security

### "Authentication failed" al probar
→ Verifica que copiaste la contraseña sin espacios (16 caracteres seguidos)

### "IMAP access is disabled"
→ Habilita IMAP en Gmail (Paso 2)

### No se encuentran correos de Netflix
→ Normal si no has recibido correos de Netflix recientemente. Envía un correo de prueba a `digitalacc06@digitalstoretrujillo.store` y verifica que llegue a Gmail.

---

## 📚 Documentación Completa

- `CONFIGURACION-GMAIL.md` - Guía detallada de Gmail
- `CAMBIOS-MULTI-PROVEEDOR.md` - Resumen técnico de cambios
- `README.md` - Documentación general

---

**Tiempo total estimado**: ⏱️ 5 minutos
