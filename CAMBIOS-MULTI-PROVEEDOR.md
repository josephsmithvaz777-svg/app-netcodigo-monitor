# 📝 Resumen de Cambios - Soporte Multi-Proveedor

## 🎯 Objetivo
Modificar la aplicación Netflix Monitor para soportar correos recibidos a través de **Cloudflare Email Routing** en el dominio `digitalstoretrujillo.store`.

## 📧 Configuración de Correos

### Cloudflare Email Routing
- `digitalacc06@digitalstoretrujillo.store` → reenvía a → `digitalstoretrujillo@gmail.com`
- `digitalacc08@digitalstoretrujillo.store` → reenvía a → `digitalstoretrujillo@gmail.com`

### Cuentas Configuradas
1. `digitalstoretrujillo05@outlook.com` (Outlook)
2. `digitalstoretrujillo03@outlook.com` (Outlook)
3. `digitalstoretrujillo@gmail.com` (Gmail - recibe correos de Cloudflare)

---

## 🔧 Cambios Realizados

### 1. **outlook_service.py** - Soporte Multi-Proveedor

#### Antes:
- Solo soportaba Outlook
- Clase: `OutlookIMAPService`
- Servidor hardcodeado: `outlook.office365.com:993`

#### Después:
- Soporta múltiples proveedores: **Outlook**, **Gmail**, **IMAP personalizado**
- Nueva clase: `IMAPService` (con alias `OutlookIMAPService` para compatibilidad)
- Configuración dinámica de servidor según proveedor
- Nueva clase: `EmailMonitor` (con alias `OutlookMonitor` para compatibilidad)

#### Proveedores Soportados:
```python
IMAP_SERVERS = {
    'outlook': {
        'server': 'outlook.office365.com',
        'port': 993
    },
    'gmail': {
        'server': 'imap.gmail.com',
        'port': 993
    },
    'custom': {
        'server': None,  # Especificar en accounts.json
        'port': 993
    }
}
```

### 2. **accounts.json** - Nuevo Formato

#### Antes:
```json
{
  "accounts": [
    {
      "email": "cuenta@outlook.com",
      "password": "contraseña"
    }
  ]
}
```

#### Después:
```json
{
  "accounts": [
    {
      "email": "cuenta@outlook.com",
      "password": "contraseña",
      "provider": "outlook"
    },
    {
      "email": "cuenta@gmail.com",
      "password": "contraseña-de-aplicacion",
      "provider": "gmail"
    },
    {
      "email": "cuenta@custom.com",
      "password": "contraseña",
      "provider": "custom",
      "imap_server": "mail.custom.com",
      "imap_port": 993
    }
  ]
}
```

**Nota**: El campo `provider` es opcional. Si no se especifica, usa `outlook` por defecto (compatibilidad con configuraciones antiguas).

### 3. **README.md** - Documentación Actualizada

- ✅ Actualizado título y descripción
- ✅ Agregadas características de soporte multi-proveedor
- ✅ Sección de configuración expandida con ejemplos para cada proveedor
- ✅ Instrucciones para Cloudflare Email Routing
- ✅ Referencias a guías específicas

### 4. **Nuevos Archivos Creados**

#### `CONFIGURACION-GMAIL.md`
Guía detallada para configurar Gmail:
- Activar verificación en dos pasos
- Generar contraseña de aplicación
- Habilitar IMAP
- Verificar Cloudflare Email Routing
- Solución de problemas

#### `test_gmail.py`
Script de prueba interactivo para:
- Verificar conexión a Gmail
- Buscar correos de Netflix
- Mostrar resultados
- Diagnóstico de errores

#### `accounts.json.cloudflare-example`
Archivo de ejemplo con configuraciones para Cloudflare Email Routing

---

## 🚀 Próximos Pasos

### 1. Configurar Gmail

Sigue la guía en `CONFIGURACION-GMAIL.md`:

1. **Generar contraseña de aplicación**:
   - Ve a: https://myaccount.google.com/apppasswords
   - Genera una contraseña para "Netflix Monitor"

2. **Habilitar IMAP**:
   - Gmail → Configuración → Reenvío y correo POP/IMAP
   - Habilitar IMAP

3. **Actualizar `accounts.json`**:
   ```json
   {
       "email": "digitalstoretrujillo@gmail.com",
       "password": "TU_CONTRASEÑA_DE_16_CARACTERES",
       "provider": "gmail"
   }
   ```

### 2. Probar la Conexión

```bash
python test_gmail.py
```

Este script te pedirá:
- Correo de Gmail
- Contraseña de aplicación

Y verificará:
- ✅ Conexión IMAP exitosa
- ✅ Búsqueda de correos de Netflix
- ✅ Extracción de códigos

### 3. Ejecutar la Aplicación

```bash
python app.py
```

Luego abre: http://localhost:5000

---

## 📊 Compatibilidad

### ✅ Retrocompatibilidad
- Los archivos `accounts.json` antiguos (sin campo `provider`) siguen funcionando
- Se usa `outlook` como proveedor por defecto
- Las clases antiguas (`OutlookIMAPService`, `OutlookMonitor`) siguen disponibles como alias

### ✅ Nuevas Funcionalidades
- Soporte para Gmail
- Soporte para Cloudflare Email Routing
- Soporte para servidores IMAP personalizados
- Configuración flexible por cuenta

---

## 🔍 Verificación de Cloudflare Email Routing

Para confirmar que Cloudflare está reenviando correctamente:

1. **Envía un correo de prueba** a `digitalacc06@digitalstoretrujillo.store`

2. **Verifica en Gmail** (`digitalstoretrujillo@gmail.com`):
   - Deberías ver el correo
   - En el encabezado verás:
     ```
     To: digitalacc06@digitalstoretrujillo.store
     Delivered-To: digitalstoretrujillo@gmail.com
     ```

3. **La aplicación detectará** correos dirigidos a cualquiera de estas direcciones:
   - `digitalacc06@digitalstoretrujillo.store`
   - `digitalacc08@digitalstoretrujillo.store`
   - `digitalstoretrujillo@gmail.com`

---

## ⚠️ Notas Importantes

### Límites de Gmail
- **Conexiones IMAP**: ~100 por hora
- **Intervalo recomendado**: 300 segundos (5 minutos)
- **Configuración actual**: `settings.json` → `check_interval: 300`

### Seguridad
- ✅ Usa contraseñas de aplicación (no contraseñas principales)
- ✅ `accounts.json` está en `.gitignore`
- ✅ Nunca compartas `accounts.json`

### Cloudflare Email Routing
- ✅ Gratuito para uso personal
- ✅ Sin límites de reenvío
- ✅ Configuración en: https://dash.cloudflare.com → Email Routing

---

## 📞 Soporte

Si encuentras problemas:

1. **Revisa los logs** en la consola de la aplicación
2. **Ejecuta el test**: `python test_gmail.py`
3. **Consulta las guías**:
   - `CONFIGURACION-GMAIL.md` - Configuración de Gmail
   - `README.md` - Documentación general
   - `accounts.json.cloudflare-example` - Ejemplos de configuración

---

**¡Listo para usar!** 🎉

La aplicación ahora puede monitorear correos de Netflix que lleguen a través de:
- Cuentas de Outlook directas
- Cuentas de Gmail directas
- Cloudflare Email Routing → Gmail/Outlook
- Cualquier servidor IMAP personalizado
