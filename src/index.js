const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const path = require('path');
const fs = require('fs');
const multer = require('multer');
const ImapService = require('./imapService');
const MailgunService = require('./mailgunService');

const app = express();
const server = http.createServer(app);
const io = new Server(server);
const upload = multer(); // Para procesar multipart/form-data de Mailgun

// Configuración
const PORT = process.env.PORT || 3000;
const accountsPath = path.join(__dirname, 'accounts.json');
const settingsPath = path.join(__dirname, 'settings.json'); // Para guardar API Keys

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, '../public')));
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, '../views'));

// Estado
let accounts = [];
let imapService = null;
let settings = { mode: 'imap', mailgunSigningKey: '', monitoredEmail: '' }; // mode: 'imap' | 'mailgun'
const latestCodes = {}; // Clave: email, Valor: { code, type, timestamp }

// Funciones Helper
function loadData() {
    if (fs.existsSync(accountsPath)) {
        try {
            accounts = JSON.parse(fs.readFileSync(accountsPath, 'utf8'));
        } catch (err) { accounts = []; }
    }
    
    // Cargar desde Variables de Entorno (Prioridad o Fallback)
    if (process.env.IMAP_USER && process.env.IMAP_PASSWORD) {
        // Si hay ENV vars, sobrescriben o crean la cuenta maestra
        accounts = [{
            user: process.env.IMAP_USER,
            pass: process.env.IMAP_PASSWORD,
            host: process.env.IMAP_HOST || 'imap.gmail.com',
            port: parseInt(process.env.IMAP_PORT) || 993,
            secure: true
        }];
    }

    if (fs.existsSync(settingsPath)) {
        try {
            settings = JSON.parse(fs.readFileSync(settingsPath, 'utf8'));
        } catch (err) { }
    }
    
    // Cargar Settings desde Variables de Entorno
    if (process.env.APP_MODE) settings.mode = process.env.APP_MODE;
    if (process.env.MONITORED_EMAIL) settings.monitoredEmail = process.env.MONITORED_EMAIL;
}

function saveData() {
    fs.writeFileSync(accountsPath, JSON.stringify(accounts, null, 2));
    fs.writeFileSync(settingsPath, JSON.stringify(settings, null, 2));
}

async function restartServices() {
    // 1. Limpiar IMAP si existe
    if (imapService) {
        await imapService.disconnectAll();
        imapService = null;
    }

    // 2. Si el modo es IMAP y hay cuentas, iniciar IMAP
    if (settings.mode === 'imap' && accounts.length > 0) {
        imapService = new ImapService(accounts);
        imapService.on('code', (data) => {
            latestCodes[data.email] = data;
            io.emit('new-code', data);
        });
        imapService.connectAll();
    }
}

// Inicialización
loadData();
restartServices();

// Servicios
const mailgunService = new MailgunService(settings.mailgunSigningKey);

// Rutas Vistas
app.get('/', (req, res) => {
    const codesList = Object.values(latestCodes).sort((a, b) => b.timestamp - a.timestamp);
    res.render('index', { 
        codes: codesList, 
        accounts: settings.mode === 'imap' ? accounts.map(a => a.user) : (settings.monitoredEmail ? [`Mailgun: ${settings.monitoredEmail}`] : ['Mailgun Webhook']),
        mode: settings.mode
    });
});

app.get('/settings', (req, res) => {
    res.render('settings', { accounts, settings });
});

// Rutas API Settings
app.post('/api/settings/mode', async (req, res) => {
    const { mode, mailgunSigningKey } = req.body;
    settings.mode = mode;
    if (mailgunSigningKey !== undefined) settings.mailgunSigningKey = mailgunSigningKey;
    
    // Actualizar servicio de mailgun con nueva key
    mailgunService.signingKey = settings.mailgunSigningKey;
    
    saveData();
    await restartServices();
    res.json({ success: true });
});

// Rutas API Accounts (IMAP)
app.post('/api/accounts', async (req, res) => {
    const { user, pass, host, port, secure } = req.body;
    if (!user || !pass || !host || !port) return res.status(400).json({ error: 'Faltan datos' });
    
    // Verificar si la cuenta ya existe para actualizarla o agregarla
    const existingIndex = accounts.findIndex(a => a.user === user);
    
    const newAccount = {
        user,
        pass,
        host,
        port: parseInt(port),
        secure: secure === 'on' || secure === true
    };

    if (existingIndex >= 0) {
        accounts[existingIndex] = newAccount; // Actualizar
    } else {
        accounts.push(newAccount); // Agregar nueva
    }
    
    settings.mode = 'imap'; // Forzar modo IMAP al agregar cuenta
    saveData();
    await restartServices();
    res.json({ success: true });
});

app.post('/api/test-connection', async (req, res) => {
    const { user, pass, host, port, secure } = req.body;
    if (!user || !pass || !host || !port) return res.status(400).json({ error: 'Faltan datos' });

    const account = { 
        user, 
        pass, 
        host, 
        port: parseInt(port), 
        secure: secure === 'on' || secure === true 
    };

    console.log(`Probando conexión para: ${user}...`);
    const result = await ImapService.testConnection(account);
    res.json(result);
});

app.delete('/api/accounts/:email', async (req, res) => {
    const emailToDelete = req.params.email;
    accounts = accounts.filter(a => a.user !== emailToDelete);
    saveData();
    await restartServices();
    res.json({ success: true });
});

// WEBHOOK MAILGUN
app.get('/webhooks/mailgun', (req, res) => {
    res.status(200).send('Mailgun Webhook is active');
});

app.post('/webhooks/mailgun', upload.any(), (req, res) => {
    // Mailgun envía datos en body (multipart parseado por multer)
    // Los campos principales son 'signature', 'token', 'timestamp', 'body-plain', etc.
    const body = req.body;

    if (!body || !body.signature) {
        return res.status(400).send('Missing signature');
    }

    // Verificar firma
    const { timestamp, token, signature } = body.signature instanceof Object ? body.signature : {
        timestamp: body['timestamp'],
        token: body['token'],
        signature: body['signature']
    };

    // Nota: Multer pone los campos simples en req.body
    // Mailgun a veces anida signature[timestamp], etc. o lo manda plano.
    // Ajuste: si body.signature es string, es estructura vieja/plana. Si no, es objeto.
    // Vamos a asumir estructura aplanada si llega por multer fields, 
    // pero si Mailgun manda JSON, express.json() lo capturó.
    
    // Unificación de parámetros de firma
    const ts = body['signature[timestamp]'] || body.timestamp;
    const tok = body['signature[token]'] || body.token;
    const sig = body['signature[signature]'] || body.signature;

    if (settings.mailgunSigningKey && !mailgunService.verifySignature(ts, tok, sig)) {
        console.warn('Firma Mailgun inválida');
        return res.status(401).send('Invalid signature');
    }

    // Procesar contenido
    console.log('Recibido webhook de Mailgun. Procesando...');
    const result = mailgunService.parsePayload(body);

    if (result.valid) {
        console.log(`Mailgun Webhook: Código para ${result.data.email}`);
        latestCodes[result.data.email] = result.data;
        io.emit('new-code', result.data);
    } else {
        console.log('Mailgun Webhook: Correo recibido sin código válido');
        // Emitir evento de log para depuración en frontend si fuera necesario
        console.log('Subject:', body['subject']);
        console.log('Text preview:', (body['body-plain'] || '').substring(0, 100));
    }

    res.status(200).send('OK');
});

// Socket.io
io.on('connection', (socket) => {
    socket.emit('init-state', Object.values(latestCodes));
});

server.listen(PORT, () => {
    console.log(`Servidor corriendo en http://localhost:${PORT}`);
});
