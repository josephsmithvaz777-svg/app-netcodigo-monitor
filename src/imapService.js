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
            
            // Buscar el último mensaje (UID más alto = más reciente)
            // Ya no filtramos por NO LEÍDO para evitar perder correos si se abrieron en otro lado
            const message = await client.fetchOne('*', { source: true, envelope: true, uid: true });
            
            if (!message || !message.source) {
                console.log('No se encontró ningún mensaje.');
                return;
            }

            // Opcional: Marcar como leído para tener control, aunque ya lo procesamos igual
            try {
                await client.messageFlagsAdd(message.uid, ['\\Seen']);
            } catch (e) { /* Ignorar error si falla marcar */ }

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

            console.log(`📩 Procesando correo de: ${originalAccount} | Asunto: ${subject}`);

            // 1. Intentar buscar enlace de verificación primero (Prioridad para Hogar/Viajero)
            // Esto evita leer números falsos del texto (como nombres de perfil con números)
            let code = null;
            // Patrón para capturar el enlace de "update-household" o "travel/verify" o "update-primary-location"
            // Se ha ampliado para capturar más variantes de URLs de Netflix
            const linkMatch = html.match(/href=["'](https:\/\/[^"']*netflix\.com\/account\/(?:travel|update-household|household|update-primary-location)\/[^"']*)["']/i);
            
            if (linkMatch) {
                const url = linkMatch[1].replace(/&amp;/g, '&'); // Decodificar ampersands
                
                // Si el usuario pide explícitamente solo el enlace y no el código:
                console.log(`🔗 Enlace detectado: ${url}`);
                code = url; 
                
                // NOTA: Antes intentábamos hacer "fetchUrlAndExtractCode(url)" para sacar el 1234.
                // Pero el usuario prefiere recibir la URL directa para hacer clic manualmente o enviársela al cliente.
                // Así que devolvemos la URL tal cual como si fuera el "código".
            }

            // Si no hay enlace (o falló), buscar código numérico en el texto (Para Login estándar)
            if (!code) {
                // Mejora: Buscar patrones numéricos con más flexibilidad (saltos de línea, espacios raros)
                code = this.extractCode(text) || this.extractCode(html);
            }

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

    async fetchUrlAndExtractCode(url) {
        try {
            console.log(`🌍 Visitando enlace para obtener código: ${url}`);
            // Headers para parecer un navegador normal
            const response = await fetch(url, {
                headers: {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                }
            });
            
            if (!response.ok) {
                console.error(`Error HTTP al visitar enlace: ${response.status}`);
                return null;
            }

            const body = await response.text();
            
            // Buscar código en el HTML de la página de respuesta
            // Generalmente es un número grande o dentro de un div específico
            // Reusamos extractCode pero con cuidado, ya que el HTML es grande
            
            // Intentar buscar patrones específicos de la web de Netflix
            // <div class="code">1234</div> o similar
            
            // Limpieza básica de HTML tags para dejar solo texto visible podría ayudar
            // pero regex directo suele ser mejor para "4 dígitos aislados"
            
            return this.extractCode(body);

        } catch (err) {
            console.error('Error obteniendo código del enlace:', err.message);
            return null;
        }
    }

    extractCode(text) {
        if (!text) return null;
        
        // Pre-limpieza para evitar que palabras se peguen al quitar tags
        // Reemplazar cierres de bloque comunes por espacios
        let processedText = text
            .replace(/<\/(div|p|h[1-6]|tr|li)>/gi, ' ') 
            .replace(/<br\s*\/?>/gi, ' ');

        // Limpiar HTML tags de forma más agresiva y normalizar espacios
        const cleanText = processedText
            .replace(/<[^>]*>/g, ' ')      // Quitar tags HTML
            .replace(/&nbsp;/gi, ' ')      // Quitar entidad espacio duro
            .replace(/[\u00A0\u1680\u180e\u2000-\u200b\u202f\u205f\u3000]/g, ' ') // Quitar otros espacios unicode
            .replace(/\s+/g, ' ')          // Colapsar espacios múltiples
            .trim();

        // 1. Prioridad: Buscar "Ingresa este código..." seguido de 4 dígitos
        // El usuario reporta: "el cuerpo del correo siempre sera Ingresa este código para iniciar sesión y luego el codigo 8102"
        // Agregamos tolerancia a dos puntos o guiones: "código: 1234"
        const phraseMatch = cleanText.match(/Ingresa este c[óo]digo.*?(?:[:\-]|\s)(\d{4})\b/i);
        if (phraseMatch) {
            if (!phraseMatch[1].match(/^202[0-9]$/)) {
                return phraseMatch[1];
            }
        }

        // 2. Patrón "8 1 9 1" (dígitos separados por espacio)
        // Buscamos 4 dígitos separados por espacios
        const spacedDigits = cleanText.match(/(\d)\s+(\d)\s+(\d)\s+(\d)/);
        if (spacedDigits) {
            return `${spacedDigits[1]}${spacedDigits[2]}${spacedDigits[3]}${spacedDigits[4]}`;
        }

        // 3. Patrón genérico de 4 dígitos (con protecciones extra)
        // Buscamos 4 dígitos que NO sean un año (2020-2029) y que tengan bordes de palabra
        const fourDigits = cleanText.match(/\b(?!202[0-9])(\d{4})\b/);
        
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
