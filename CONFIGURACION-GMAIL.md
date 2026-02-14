# 🔧 Configuración de Gmail para la App Netflix Monitor

## ✅ Resumen de Configuración Actual

Tu configuración de Cloudflare Email Routing:
- `digitalacc06@digitalstoretrujillo.store` → reenvía a → `digitalstoretrujillo@gmail.com`
- `digitalacc08@digitalstoretrujillo.store` → reenvía a → `digitalstoretrujillo@gmail.com`

La aplicación monitoreará la cuenta de Gmail `digitalstoretrujillo@gmail.com` donde llegarán todos los correos de Netflix.

---

## 📋 Pasos para Configurar Gmail

### 1. Activar Verificación en Dos Pasos

1. Ve a: https://myaccount.google.com/security
2. En la sección "Cómo accedes a Google", haz clic en **"Verificación en dos pasos"**
3. Si no está activada, actívala siguiendo los pasos
4. **Importante**: Debes tener la verificación en dos pasos activa para poder generar contraseñas de aplicación

### 2. Generar Contraseña de Aplicación

1. Ve a: https://myaccount.google.com/apppasswords
   - O desde https://myaccount.google.com/security → busca "Contraseñas de aplicaciones"
2. En "Selecciona la app", elige **"Correo"** o **"Otra (nombre personalizado)"**
   - Si eliges "Otra", escribe: `Netflix Monitor`
3. En "Selecciona el dispositivo", elige **"Otro (nombre personalizado)"**
   - Escribe: `Python IMAP`
4. Haz clic en **"Generar"**
5. Google te mostrará una contraseña de 16 caracteres (sin espacios)
   - Ejemplo: `abcd efgh ijkl mnop` (cópiala sin los espacios: `abcdefghijklmnop`)

### 3. Actualizar accounts.json

Abre el archivo `accounts.json` y reemplaza `TU_CONTRASEÑA_DE_APLICACION_GMAIL_AQUI` con la contraseña generada:

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
            "email": "digitalstoretrujillo@gmail.com",
            "password": "abcdefghijklmnop",
            "provider": "gmail"
        }
    ]
}
```

### 4. Habilitar IMAP en Gmail (si no está habilitado)

1. Ve a Gmail: https://mail.google.com
2. Haz clic en el ícono de **configuración** (⚙️) → **Ver toda la configuración**
3. Ve a la pestaña **"Reenvío y correo POP/IMAP"**
4. En la sección **"Acceso IMAP"**, selecciona **"Habilitar IMAP"**
5. Haz clic en **"Guardar cambios"**

---

## 🚀 Probar la Configuración

Una vez configurado, ejecuta:

```bash
python app.py
```

Luego abre http://localhost:5000 y haz clic en **"Verificar Ahora"** para buscar correos de Netflix.

---

## 🔍 Verificar que Cloudflare está Reenviando Correctamente

Para confirmar que los correos están llegando a Gmail:

1. Ve a Gmail: https://mail.google.com
2. Busca correos de Netflix
3. Verifica que veas correos dirigidos a:
   - `digitalacc06@digitalstoretrujillo.store`
   - `digitalacc08@digitalstoretrujillo.store`
4. En el encabezado del correo, deberías ver algo como:
   ```
   To: digitalacc06@digitalstoretrujillo.store
   Delivered-To: digitalstoretrujillo@gmail.com
   ```

---

## ⚠️ Solución de Problemas

### Error: "Authentication failed"
- ✅ Verifica que la verificación en dos pasos esté activa
- ✅ Genera una nueva contraseña de aplicación
- ✅ Asegúrate de copiar la contraseña sin espacios

### Error: "IMAP access is disabled"
- ✅ Habilita IMAP en la configuración de Gmail (ver paso 4)

### No se encuentran correos de Netflix
- ✅ Verifica que Cloudflare Email Routing esté configurado correctamente
- ✅ Envía un correo de prueba a `digitalacc06@digitalstoretrujillo.store` y verifica que llegue a Gmail
- ✅ Asegúrate de que los correos de Netflix no estén en spam

---

## 📝 Notas Importantes

- **Seguridad**: La contraseña de aplicación es específica para esta app. Si la revocas, la app dejará de funcionar.
- **Límites de Gmail**: Gmail permite ~100 conexiones IMAP por hora. El intervalo recomendado es de 5 minutos (300 segundos).
- **Cloudflare Email Routing**: Es gratuito y no tiene límites de reenvío para uso personal.

---

**¡Listo!** Una vez configurado, la aplicación monitoreará automáticamente los correos de Netflix que lleguen a través de Cloudflare Email Routing. 🎉
