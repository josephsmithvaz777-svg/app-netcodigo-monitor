# 🚀 Guía de Inicio Rápido

## ✅ Dependencias ya instaladas

Las dependencias de Python ya están instaladas correctamente.

## 📝 SIGUIENTE PASO: Configurar tus cuentas de Outlook

### Opción 1: Editar directamente el archivo

Abre `accounts.json` y añade tus cuentas:

```json
{
  "accounts": [
    {
      "email": "cuenta1@outlook.com",
      "password": "CONTRASEÑA-DE-APLICACION-AQUI"
    },
    {
      "email": "cuenta2@outlook.com",
      "password": "CONTRASEÑA-DE-APLICACION-AQUI"
    }
  ]
}
```

### ⚠️ MUY IMPORTANTE: Necesitas una Contraseña de Aplicación

Para que IMAP funcione con Outlook, **NO uses tu contraseña normal de Outlook**. Necesitas generar una **Contraseña de Aplicación**:

#### Pasos para crear una Contraseña de Aplicación en Microsoft:

1. **Ve a tu cuenta de Microsoft**: https://account.microsoft.com/security

2. **Activa la verificación en dos pasos** (si no está activa):
   - Haz clic en "Opciones de seguridad avanzadas"
   - Activa "Verificación en dos pasos"

3. **Genera una contraseña de aplicación**:
   - En la misma página, busca "Contraseñas de aplicación"
   - Haz clic en "Crear una nueva contraseña de aplicación"
   - Se generará un código como: `abcd efgh ijkl mnop`
   - **COPIA ESTE CÓDIGO** (no incluyas los espacios)

4. **Usa este código en `accounts.json`**:
   ```json
   {
     "email": "tucuenta@outlook.com",
     "password": "abcdefghijklmnop"
   }
   ```

### Verificar que IMAP esté habilitado

1. Ve a https://outlook.live.com/mail/
2. Haz clic en el ícono de configuración (⚙️)
3. Ve a "Ver toda la configuración de Outlook"
4. Selecciona "Correo" > "Sincronizar correo"
5. Asegúrate que **"Permitir que los dispositivos y aplicaciones usen POP"** o **IMAP** esté habilitado

## 🎯 Ejecutar la aplicación

Una vez que hayas configurado `accounts.json` con tus credenciales:

```bash
python app.py
```

Luego abre tu navegador en: **http://localhost:5000**

## 🔍 ¿Qué tan rápido es IMAP?

**Respuesta corta:** Muy rápido - 2 a 5 segundos por cuenta.

- ✅ **Verificación manual**: Instantánea (haz clic en "Verificar Ahora")
- ✅ **Verificación automática**: Configurable (recomendado: cada 60-300 segundos)
- ✅ **Múltiples cuentas**: Se procesan en paralelo

### Recomendaciones de frecuencia:

- **60 segundos (1 minuto)**: Para monitoreo muy frecuente (cuidado con límites de Microsoft)
- **180 segundos (3 minutos)**: Equilibrio ideal entre velocidad y seguridad
- **300 segundos (5 minutos)**: Muy seguro, sin riesgo de bloqueos

Microsoft permite ~100 conexiones IMAP por hora por cuenta, así que con 300 segundos (5 minutos) estás muy seguro.

## 🎨 Características de la Interfaz

- **Dashboard en tiempo real** con actualizaciones vía WebSocket
- **Estadísticas visuales**: Total de correos, códigos de inicio, temporales, actualizaciones
- **Filtros inteligentes**: Por tipo de correo y por cuenta
- **Copia rápida**: Haz clic para copiar códigos al portapapeles
- **Tema oscuro estilo Netflix**: Moderno y profesional
- **Notificaciones**: Sonido y notificaciones del navegador para nuevos correos

## 🔧 Solución rápida de problemas

### Error: "Authentication failed"
- Verifica que estés usando la **contraseña de aplicación**, NO tu contraseña normal de Outlook
- Asegúrate que la verificación en dos pasos esté activa

### Error: "No module named 'flask'"
- Ejecuta de nuevo: `pip install -r requirements.txt`

### No se encuentran correos
- Verifica que los correos sean de `@netflix.com`
- Asegúrate que estén en la bandeja de entrada (INBOX)
- Aumenta `days_back` en `settings.json` si los correos son antiguos

## 📧 Contacto

Si tienes problemas, revisa el archivo `README.md` para más detalles.

---

**¡Listo para empezar! 🎉**
