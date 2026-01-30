# Cambiar a Modo "Gmail Master Account" (codesnetfl@gmail.com)

El plan es reconfigurar la aplicación para que **deje de usar Mailgun** y vuelva a usar el sistema **IMAP**, pero conectado exclusivamente a `codesnetfl@gmail.com`.

## 1. Modificar Configuración (`settings.json`)
*   Cambiar `mode` de `"mailgun"` a `"imap"`.
*   Esto le dice a la aplicación que use el `ImapService.js` en lugar de esperar webhooks.

## 2. Configurar la Cuenta Maestra (`accounts.json`)
*   Actualizar la lista de cuentas para que solo tenga **una** entrada: `codesnetfl@gmail.com`.
*   **Importante:** Necesitaremos una **Contraseña de Aplicación** de Google para esta cuenta (no tu contraseña normal).

## 3. Lógica de Detección de Destinatario
*   El código actual (`ImapService.js`) ya tiene una función inteligente (`fetchLatest`) que busca frases como "Enviado a: usuario@netflix.com" dentro del cuerpo del correo.
*   Esto es perfecto para los correos reenviados, ya que Gmail suele incluir el encabezado original en el texto del mensaje reenviado.
*   No hace falta modificar código complejo, solo asegurar que la configuración apunte a esta cuenta.

## Pasos para ti (Usuario):
1.  **Generar Contraseña de Aplicación:** Ve a tu cuenta Google `codesnetfl@gmail.com` > Seguridad > Verificación en 2 pasos > Contraseñas de aplicaciones. Crea una y anótala.
2.  **Configurar Reenvío:** Asegúrate de que tus 20+ cuentas de Netflix estén reenviando los correos a `codesnetfl@gmail.com`.

¿Te parece bien este plan? Si confirmas, procederé a editar los archivos de configuración.