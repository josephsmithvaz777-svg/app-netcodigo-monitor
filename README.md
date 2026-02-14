# 📧 Netflix Codes Monitor - Monitor de Códigos de Netflix

Aplicación web en Python que monitorea múltiples cuentas de correo vía IMAP (Outlook, Gmail, y otros) para detectar y mostrar automáticamente correos de Netflix relacionados con:

- 🔑 **Códigos de inicio de sesión**
- ⏱️ **Códigos temporales**
- 🏠 **Actualizaciones de hogar**

## ✨ Características

- ✅ Soporte para múltiples proveedores: **Outlook**, **Gmail**, y **IMAP personalizado**
- ✅ Compatible con **Cloudflare Email Routing** (reenvío a Gmail/Outlook)
- ✅ Conexión directa vía IMAP (sin necesidad de redireccionar correos manualmente)
- ✅ Monitoreo de múltiples cuentas simultáneamente
- ✅ Interfaz web moderna con tema oscuro estilo Netflix
- ✅ Actualizaciones en tiempo real con WebSockets
- ✅ Filtrado por tipo de correo y cuenta
- ✅ Extracción automática de códigos
- ✅ Notificaciones de nuevos correos
- ✅ Consultas rápidas (2-5 segundos por cuenta)

## 🚀 Instalación Rápida

### 1. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar Cuentas de Correo

Copia el archivo de ejemplo y edítalo con tus credenciales:

```bash
copy accounts.json.example accounts.json
```

Edita `accounts.json` y especifica el proveedor para cada cuenta:

```json
{
  "accounts": [
    {
      "email": "cuenta1@outlook.com",
      "password": "tu-contraseña-de-aplicacion",
      "provider": "outlook"
    },
    {
      "email": "tucorreo@gmail.com",
      "password": "tu-contraseña-de-aplicacion",
      "provider": "gmail"
    },
    {
      "email": "correo@tudominio.com",
      "password": "tu-contraseña",
      "provider": "custom",
      "imap_server": "mail.tudominio.com",
      "imap_port": 993
    }
  ]
}
```

#### 📧 Configuración por Proveedor:

**Outlook/Microsoft 365:**
1. Ve a https://account.microsoft.com/security
2. Activa la verificación en dos pasos
3. Ve a "Contraseñas de aplicación"
4. Genera una nueva contraseña para "IMAP"
5. Usa `"provider": "outlook"` en accounts.json

**Gmail/Google Workspace:**
1. Ve a https://myaccount.google.com/security
2. Activa la verificación en dos pasos
3. Ve a https://myaccount.google.com/apppasswords
4. Genera una contraseña de aplicación
5. Habilita IMAP en configuración de Gmail
6. Usa `"provider": "gmail"` en accounts.json
7. **Ver guía detallada**: [CONFIGURACION-GMAIL.md](CONFIGURACION-GMAIL.md)

**Cloudflare Email Routing:**
- Configura el reenvío en Cloudflare a Gmail u Outlook
- Usa la cuenta de destino (Gmail/Outlook) en accounts.json
- Ejemplo: `digitalacc06@tudominio.com` → reenvía a → `tucorreo@gmail.com`
- Configura `tucorreo@gmail.com` con `"provider": "gmail"`

**Otros proveedores IMAP:**
- Usa `"provider": "custom"`
- Especifica `"imap_server"` y `"imap_port"`

### 3. Configurar Ajustes (Opcional)

El archivo `settings.json` ya está configurado con valores recomendados:

```json
{
  "check_interval": 300,        // Verificar cada 5 minutos (mínimo 60 segundos)
  "days_back": 7,                // Buscar correos de los últimos 7 días
  "auto_mark_read": false,       // No marcar como leídos automáticamente
  "notification_enabled": true   // Notificaciones habilitadas
}
```

### 4. Ejecutar la Aplicación

```bash
python app.py
```

La aplicación estará disponible en: **http://localhost:5000**

## 📖 Uso

### Inicio Rápido

1. **Abrir la aplicación** en tu navegador: http://localhost:5000
2. **Verificar cuentas**: Haz clic en el ícono de configuración (⚙️) para ver las cuentas configuradas
3. **Verificación manual**: Haz clic en "Verificar Ahora" para buscar correos inmediatamente
4. **Monitoreo automático**: Haz clic en "Iniciar Monitoreo" para verificar automáticamente cada X segundos

### Funciones Principales

#### 🔍 Verificación Manual
- Haz clic en **"Verificar Ahora"** para buscar correos instantáneamente
- Tiempo de respuesta: 2-5 segundos por cuenta
- No afecta el monitoreo automático

#### 🔄 Monitoreo Automático
- Haz clic en **"Iniciar Monitoreo"** para comenzar
- La aplicación verificará automáticamente según el intervalo configurado
- **Recomendado**: 60-300 segundos (1-5 minutos)
- Recibirás notificaciones de nuevos correos

#### 🎯 Filtros
- **Por tipo**: Códigos de inicio, temporales o actualización de hogar
- **Por cuenta**: Ver correos de una cuenta específica

#### 📋 Copiar Códigos
- Haz clic en el ícono de copiar (📋) para copiar el código al portapapeles

### ⚙️ Configuración

Haz clic en el ícono de configuración para ajustar:

- **Intervalo de verificación**: Tiempo entre verificaciones automáticas (mínimo 60 segundos)
- **Días hacia atrás**: Cuántos días buscar en el historial (1-30 días)
- **Notificaciones**: Activar/desactivar notificaciones de nuevos correos

## 🔧 Configuración Avanzada

### Variables de Entorno

Puedes crear un archivo `.env` para configuraciones adicionales:

```env
PORT=5000
SECRET_KEY=tu-clave-secreta-aqui
DEBUG=False
```

### Ajustar Límites de Tasa

Si experimentas bloqueos por parte de Outlook:

1. Aumenta el `check_interval` a 300 segundos (5 minutos) o más
2. Reduce el número de cuentas monitoreadas simultáneamente
3. Considera usar horarios específicos para monitoreo

## 📊 Arquitectura

```
┌─────────────────┐
│  Navegador Web  │
│   (JavaScript)  │
└────────┬────────┘
         │ WebSocket/HTTP
         │
┌────────▼────────┐
│  Flask Server   │
│   (app.py)      │
└────────┬────────┘
         │
┌────────▼────────┐
│  Outlook IMAP   │
│    Service      │
│(outlook_service)│
└────────┬────────┘
         │
┌────────▼────────┐
│ Outlook Servers │
│  (IMAP 993)     │
└─────────────────┘
```

### Componentes

- **app.py**: Servidor Flask con Socket.IO para actualizaciones en tiempo real
- **outlook_service.py**: Servicio IMAP para conectar a Outlook y filtrar correos
- **templates/index.html**: Interfaz web moderna
- **static/css/style.css**: Estilos con tema oscuro estilo Netflix
- **static/js/app.js**: Lógica frontend con WebSockets

## 🛠️ Solución de Problemas

### Error: "Authentication failed"

- ✅ Verifica que estés usando una **contraseña de aplicación**, no tu contraseña normal
- ✅ Asegúrate que la verificación en dos pasos esté activa en tu cuenta Microsoft
- ✅ Genera una nueva contraseña de aplicación

### Error: "Connection timeout"

- ✅ Verifica tu conexión a internet
- ✅ Comprueba que el firewall no bloquee el puerto 993 (IMAP SSL)
- ✅ Algunos países/redes bloquean IMAP, considera usar VPN

### No se encuentran correos de Netflix

- ✅ Verifica que los correos estén en la bandeja de entrada (INBOX)
- ✅ Asegúrate que sean correos recientes (dentro del rango de `days_back`)
- ✅ Los correos deben ser de dominios `@netflix.com`

### El monitoreo se detiene solo

- ✅ Reduce la frecuencia de verificación (aumenta `check_interval`)
- ✅ Microsoft puede estar bloqueando temporalmente por demasiadas solicitudes
- ✅ Espera 15-30 minutos antes de reintentar

## 🔒 Seguridad

- ❌ **NO** compartas el archivo `accounts.json` (contiene contraseñas)
- ✅ Usa contraseñas de aplicación en lugar de contraseñas principales
- ✅ El archivo está en `.gitignore` para evitar subirlo a Git
- ✅ Considera encriptar las contraseñas en producción

## 📝 Notas Importantes

### Rendimiento de IMAP

- **Velocidad**: 2-5 segundos por cuenta para consultas con filtros
- **Intervalo recomendado**: 60-300 segundos (1-5 minutos)
- **Límites de Microsoft**: ~100 conexiones por hora por cuenta
- **Verificación manual**: Sin límites prácticos, disponible al instante

### Tipos de Correos Detectados

La aplicación busca específicamente correos de Netflix con:

1. **Códigos de inicio**: Correos con códigos para iniciar sesión en un nuevo dispositivo
2. **Códigos temporales**: Códigos de verificación de un solo uso
3. **Actualización de hogar**: Notificaciones sobre cambios en el hogar Netflix

## 🚀 Próximas Mejoras

- [ ] Soporte para Gmail (adicional a Outlook)
- [ ] Base de datos para historial de correos
- [ ] Exportar correos a CSV/Excel
- [ ] API REST para integración con otras aplicaciones
- [ ] Soporte para más tipos de correos de Netflix
- [ ] Interfaz móvil mejorada

## 📄 Licencia

Este proyecto es de uso personal/educativo.

## 🤝 Contribuciones

¿Tienes ideas para mejorar? ¡Crea un issue o pull request!

---

**Hecho con ❤️ para simplificar el monitoreo de códigos de Netflix**
