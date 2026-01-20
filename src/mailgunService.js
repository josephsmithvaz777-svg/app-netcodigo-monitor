const crypto = require('crypto');

class MailgunService {
    constructor(signingKey) {
        this.signingKey = signingKey;
    }

    verifySignature(timestamp, token, signature) {
        if (!this.signingKey) return true; // Si no hay key configurada, saltamos validación (no recomendado prod)
        
        const encodedToken = crypto
            .createHmac('sha256', this.signingKey)
            .update(timestamp.concat(token))
            .digest('hex');

        return encodedToken === signature;
    }

    parsePayload(body) {
        // Mailgun envía el cuerpo en 'body-plain' (texto) o 'stripped-text' (sin citas)
        const text = body['body-plain'] || body['stripped-text'] || '';
        const html = body['body-html'] || '';
        const subject = body['subject'] || '';
        const recipient = body['recipient'] || ''; // El correo que recibió el mensaje (tu dominio mailgun)
        const sender = body['sender'] || ''; // De quien viene (Netflix)
        
        // Intentar sacar el destinatario original (si fue reenviado)
        // Mailgun a veces pone headers en body['message-headers'] (JSON string)
        let originalAccount = recipient;

        // Búsqueda en texto (igual que antes)
        const bodyMatch = text.match(/(?:To|Para|Enviado a):\s*([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9._-]+)/i);
        if (bodyMatch) {
            originalAccount = bodyMatch[1];
        }

        const code = this.extractCode(text) || this.extractCode(html);
        const type = this.determineType(subject, text, html);

        return {
            valid: !!code,
            data: {
                email: originalAccount,
                code: code,
                type: type,
                timestamp: new Date(),
                via: 'Mailgun Webhook'
            }
        };
    }

    extractCode(text) {
        if (!text) return null;
        const cleanText = text.replace(/\s+/g, ' ');

        // Patrón "8 1 9 1"
        const spacedDigits = cleanText.match(/\b(\d)\s+(\d)\s+(\d)\s+(\d)\b/);
        if (spacedDigits) {
            return `${spacedDigits[1]}${spacedDigits[2]}${spacedDigits[3]}${spacedDigits[4]}`;
        }

        // Patrón 4 dígitos
        const fourDigits = cleanText.match(/(?:código|code).*?\b(\d{4})\b/i);
        if (fourDigits) {
             return fourDigits[1];
        }
        return null;
    }

    determineType(subject, text, html) {
        const content = (subject + ' ' + text + ' ' + html).toLowerCase();
        if (content.includes('actuali') || content.includes('update')) return 'Actualización Hogar';
        if (content.includes('hogar') || content.includes('household')) return 'Código Hogar';
        return 'Inicio de Sesión';
    }
}

module.exports = MailgunService;
