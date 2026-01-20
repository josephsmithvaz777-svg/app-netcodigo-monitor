const { ImapFlow } = require('imapflow');
const { simpleParser } = require('mailparser');
const EventEmitter = require('events');

class ImapService extends EventEmitter {
    constructor(accounts) {
        super();
        this.accounts = accounts;
        this.connections = [];
    }

    async connectAll() {
        console.log(`Iniciando conexión con ${this.accounts.length} cuentas...`);
        for (const account of this.accounts) {
            this.connectOne(account).catch(err => {
                console.error(`Error inicial conectando a ${account.user}:`, err.message);
            });
        }
    }

    async connectOne(account) {
        const client = new ImapFlow({
            host: account.host,
            port: account.port,
            secure: account.secure,
            auth: {
                user: account.user,
                pass: account.pass
            },
            logger: false,
            emitLogs: false
        });

        client.on('error', (err) => {
            console.error(`Error en conexión de ${account.user}:`, err.message);
        });

        await client.connect();
        console.log(`✅ Conectado: ${account.user}`);

        // Abrir INBOX y mantener lock para configuración inicial
        let lock = await client.getMailboxLock('INBOX');
        try {
            // Configurar listener para nuevos correos
            client.on('exists', async (data) => {
                // Cuando llega un correo nuevo (o cambia el conteo)
                // data.count es el nuevo número de mensajes
                // data.prevCount es el anterior
                if (data.count > data.prevCount) {
                    console.log(`Nuevo correo detectado en ${account.user}`);
                    await this.fetchLatest(client, account.user);
                }
            });
        } finally {
            lock.release();
        }

        // Iniciar IDLE para recibir notificaciones en tiempo real
        // Esto mantendrá la conexión abierta y escuchando
        await client.idle();
        
        this.connections.push(client);
    }

    async disconnectAll() {
        console.log('Cerrando todas las conexiones IMAP...');
        const promises = this.connections.map(async (client) => {
            try {
                if (client) {
                    await client.logout(); // logout cierra la conexión limpiamente
                }
            } catch (err) {
                console.error('Error cerrando conexión:', err.message);
            }
        });
        
        await Promise.all(promises);
        this.connections = [];
        console.log('Todas las conexiones cerradas.');
    }

    async fetchLatest(client, userEmail) {
        // Necesitamos un lock para operar en el buzón
        let lock;
        try {
            lock = await client.getMailboxLock('INBOX');
            
            // Buscar el último mensaje
            const message = await client.fetchOne('*', { source: true, envelope: true });
            
            if (!message || !message.source) return;

            const parsed = await simpleParser(message.source);
            const subject = parsed.subject || '';
            const text = parsed.text || '';
            const html = parsed.html || '';

            // Intentar descubrir la cuenta original (quien recibió el correo originalmente)
            // 1. Revisar encabezados de reenvío estándar (X-Forwarded-To, etc) no siempre están disponibles fácil
            // 2. Revisar el campo "To" del sobre (envelope) o headers
            // 3. Buscar en el cuerpo del texto patrones de reenvío "To: cuenta@original.com"

            let originalAccount = 'Desconocido';
            
            // Estrategia 1: Buscar en el campo 'To' (si el reenvío mantiene el destinatario original en CC o similar)
            if (parsed.to && parsed.to.text) {
                 // A veces al reenviar, el 'To' sigue siendo la cuenta original si es redirección automática
                 // Pero si es reenvío manual, cambia. Asumimos redirección automática.
                 originalAccount = parsed.to.text;
            }

            // Estrategia 2: Buscar en el cuerpo del mensaje (común en reenvíos)
            // "To: cuenta@netflix.com"
            const bodyMatch = text.match(/(?:To|Para|Enviado a):\s*([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9._-]+)/i);
            if (bodyMatch) {
                originalAccount = bodyMatch[1];
            }

            // Si es la cuenta maestra, intentamos ver si hay otro indicador
            if (originalAccount.includes(userEmail)) {
                // Si detectamos que la cuenta extraída es la misma maestra, 
                // intentamos buscar otra dirección en el header 'Delivered-To' o similar si estuviera accesible,
                // pero por ahora nos fiamos de que el reenvío automático suele preservar headers o ponerlo en el cuerpo.
            }

            const code = this.extractCode(text) || this.extractCode(html);
            
            if (code) {
                const type = this.determineType(subject, text, html);
                // Usamos la cuenta original detectada en lugar de userEmail (que es la maestra)
                console.log(`Código encontrado para ${originalAccount}: ${code} (${type})`);
                
                this.emit('code', {
                    email: originalAccount, // <--- Aquí va la cuenta original
                    code: code,
                    type: type,
                    timestamp: new Date(),
                    via: userEmail // Guardamos por si acaso
                });
            }

        } catch (err) {
            console.error(`Error leyendo correo de ${userEmail}:`, err);
        } finally {
            if (lock) lock.release();
        }
    }

    extractCode(text) {
        if (!text) return null;
        
        // Limpiar HTML tags si es HTML crudo (aunque simpleParser ayuda)
        // Pero simpleParser.text ya nos da texto plano.
        
        // Buscamos patrones:
        // 1. "8 1 9 1" (dígitos separados por espacio)
        // 2. "8191" (dígitos juntos, pero aislados)
        
        // Normalizar espacios múltiples a uno solo
        const cleanText = text.replace(/\s+/g, ' ');

        // Patrón específico para "8 1 9 1"
        // \b asegura límites de palabra
        const spacedDigits = cleanText.match(/\b(\d)\s+(\d)\s+(\d)\s+(\d)\b/);
        if (spacedDigits) {
            return `${spacedDigits[1]}${spacedDigits[2]}${spacedDigits[3]}${spacedDigits[4]}`;
        }

        // Patrón para 4 dígitos juntos, ej: "Tu código es 1234"
        // Evitamos años como 2024, 2025.
        // Generalmente el código está solo o precedido por "código".
        const fourDigits = cleanText.match(/(?:código|code).*?\b(\d{4})\b/i);
        if (fourDigits) {
             return fourDigits[1];
        }

        return null;
    }

    determineType(subject, text, html) {
        const content = (subject + ' ' + text + ' ' + html).toLowerCase();
        
        if (content.includes('actuali') || content.includes('update')) {
            return 'Actualización Hogar';
        }
        if (content.includes('hogar') || content.includes('household')) {
            return 'Código Hogar';
        }
        return 'Inicio de Sesión';
    }
}

module.exports = ImapService;
