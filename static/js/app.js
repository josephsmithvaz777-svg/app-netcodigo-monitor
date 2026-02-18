// Socket.IO Connection
const socket = io();

// State
let currentEmails = [];
let currentSettings = {};
let isMonitoring = false;

// DOM Elements
const elements = {
    // Status
    connectionStatus: document.getElementById('connectionStatus'),

    // Stats
    totalEmails: document.getElementById('totalEmails'),
    codigosInicio: document.getElementById('codigosInicio'),
    codigosTemporal: document.getElementById('codigosTemporal'),
    actualizacionesHogar: document.getElementById('actualizacionesHogar'),

    // Controls
    startMonitoringBtn: document.getElementById('startMonitoringBtn'),
    stopMonitoringBtn: document.getElementById('stopMonitoringBtn'),
    checkNowBtn: document.getElementById('checkNowBtn'),

    // Filters
    typeFilter: document.getElementById('typeFilter'),

    // Emails
    emailsContainer: document.getElementById('emailsContainer'),
    lastUpdate: document.getElementById('lastUpdate'),

    // Modal
    settingsBtn: document.getElementById('settingsBtn'),
    settingsModal: document.getElementById('settingsModal'),
    closeSettingsBtn: document.getElementById('closeSettingsBtn'),
    cancelSettingsBtn: document.getElementById('cancelSettingsBtn'),
    saveSettingsBtn: document.getElementById('saveSettingsBtn'),

    // Settings Form
    checkInterval: document.getElementById('checkInterval'),
    daysBack: document.getElementById('daysBack'),
    notificationEnabled: document.getElementById('notificationEnabled'),
    accountsList: document.getElementById('accountsList'),

    // Toast
    toastContainer: document.getElementById('toastContainer')
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Aplicación iniciada');
    setupEventListeners();
    loadSettings();
    loadAccounts();
});

// Socket Events
socket.on('connect', () => {
    console.log('✅ Conectado al servidor');
    updateConnectionStatus('connected');
    showToast('Conectado al servidor', 'success');
});

socket.on('disconnect', () => {
    console.log('❌ Desconectado del servidor');
    updateConnectionStatus('disconnected');
    showToast('Desconectado del servidor', 'error');
});

socket.on('connected', (data) => {
    console.log('📡 Datos de conexión:', data);
    isMonitoring = data.monitoring_active;
    updateMonitoringUI(isMonitoring);
});

socket.on('new_emails', (data) => {
    console.log('📧 Nuevos correos recibidos:', data.count);
    showToast(`${data.count} nuevo(s) correo(s) de Netflix`, 'info');

    if (currentSettings.notification_enabled && 'Notification' in window) {
        if (Notification.permission === 'granted') {
            new Notification('Netflix Codes Monitor', {
                body: `${data.count} nuevo(s) correo(s) de Netflix`,
                icon: '/static/favicon.ico'
            });
        }
    }

    // Reproducir sonido de notificación
    playNotificationSound();
});

socket.on('emails_updated', (data) => {
    console.log('🔄 Correos actualizados:', data.total);
    elements.lastUpdate.textContent = `Última actualización: ${formatDateTime(data.timestamp)}`;
    loadEmails();
});

// Event Listeners
function setupEventListeners() {
    // Control buttons
    elements.startMonitoringBtn.addEventListener('click', startMonitoring);
    elements.stopMonitoringBtn.addEventListener('click', stopMonitoring);
    elements.checkNowBtn.addEventListener('click', checkNow);

    // Filters
    elements.typeFilter.addEventListener('change', applyFilters);

    // Modal
    elements.settingsBtn.addEventListener('click', openSettingsModal);
    elements.closeSettingsBtn.addEventListener('click', closeSettingsModal);
    elements.cancelSettingsBtn.addEventListener('click', closeSettingsModal);
    elements.saveSettingsBtn.addEventListener('click', saveSettings);

    // Close modal on outside click
    elements.settingsModal.addEventListener('click', (e) => {
        if (e.target === elements.settingsModal) {
            closeSettingsModal();
        }
    });

    // Request notification permission
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
    }
}

// Connection Status
function updateConnectionStatus(status) {
    const statusClasses = {
        'connected': 'connected',
        'monitoring': 'monitoring',
        'disconnected': ''
    };

    const statusTexts = {
        'connected': 'Conectado',
        'monitoring': 'Monitoreando',
        'disconnected': 'Desconectado'
    };

    elements.connectionStatus.className = `status-indicator ${statusClasses[status]}`;
    elements.connectionStatus.querySelector('.status-text').textContent = statusTexts[status];
}

// Monitoring Controls
async function startMonitoring() {
    try {
        showLoading(elements.startMonitoringBtn);

        const response = await fetch('/api/start', {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            isMonitoring = true;
            updateMonitoringUI(true);
            updateConnectionStatus('monitoring');
            showToast(data.message, 'success');

            // Cargar correos inmediatamente
            loadEmails();
        } else {
            showToast(data.error || 'Error al iniciar monitoreo', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('Error al iniciar monitoreo', 'error');
    } finally {
        hideLoading(elements.startMonitoringBtn);
    }
}

async function stopMonitoring() {
    try {
        showLoading(elements.stopMonitoringBtn);

        const response = await fetch('/api/stop', {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            isMonitoring = false;
            updateMonitoringUI(false);
            updateConnectionStatus('connected');
            showToast(data.message, 'success');
        } else {
            showToast(data.error || 'Error al detener monitoreo', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('Error al detener monitoreo', 'error');
    } finally {
        hideLoading(elements.stopMonitoringBtn);
    }
}

async function checkNow() {
    try {
        showLoading(elements.checkNowBtn);
        showToast('Verificando correos...', 'info');

        const response = await fetch('/api/check', {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            currentEmails = data.emails;
            renderEmails(currentEmails);
            updateStats(currentEmails);
            showToast(data.message, 'success');
        } else {
            showToast(data.error || 'Error al verificar correos', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('Error al verificar correos', 'error');
    } finally {
        hideLoading(elements.checkNowBtn);
    }
}

function updateMonitoringUI(monitoring) {
    if (monitoring) {
        elements.startMonitoringBtn.style.display = 'none';
        elements.stopMonitoringBtn.style.display = 'inline-flex';
    } else {
        elements.startMonitoringBtn.style.display = 'inline-flex';
        elements.stopMonitoringBtn.style.display = 'none';
    }
}

// Load Data
async function loadEmails() {
    try {
        const typeFilter = elements.typeFilter.value;

        let url = '/api/emails';
        const params = new URLSearchParams();

        if (typeFilter) params.append('type', typeFilter);

        if (params.toString()) {
            url += '?' + params.toString();
        }

        const response = await fetch(url);
        const data = await response.json();

        if (data.success) {
            currentEmails = data.emails;
            renderEmails(currentEmails);
            updateStats(currentEmails);
        }
    } catch (error) {
        console.error('Error al cargar correos:', error);
        showToast('Error al cargar correos', 'error');
    }
}

async function loadSettings() {
    try {
        const response = await fetch('/api/settings');
        const data = await response.json();

        if (data.success) {
            currentSettings = data.settings;

            elements.checkInterval.value = currentSettings.check_interval || 300;
            elements.daysBack.value = currentSettings.days_back || 7;
            elements.notificationEnabled.checked = currentSettings.notification_enabled || false;
        }
    } catch (error) {
        console.error('Error al cargar configuración:', error);
    }
}

async function loadAccounts() {
    try {
        const response = await fetch('/api/accounts');
        const data = await response.json();

        if (data.success) {
            // Populate accounts list in settings
            elements.accountsList.innerHTML = '';

            if (data.accounts.length === 0) {
                elements.accountsList.innerHTML = '<p style="color: var(--netflix-gray); font-size: 14px;">No hay cuentas configuradas. Edita el archivo accounts.json</p>';
            } else {
                data.accounts.forEach(account => {
                    const item = document.createElement('div');
                    item.className = 'account-item';
                    item.innerHTML = `
                        <i class="fas fa-envelope"></i>
                        <span>${account.email}</span>
                    `;
                    elements.accountsList.appendChild(item);
                });
            }
        }
    } catch (error) {
        console.error('Error al cargar cuentas:', error);
    }
}

async function saveSettings() {
    try {
        showLoading(elements.saveSettingsBtn);

        const newSettings = {
            check_interval: parseInt(elements.checkInterval.value),
            days_back: parseInt(elements.daysBack.value),
            notification_enabled: elements.notificationEnabled.checked
        };

        const response = await fetch('/api/settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(newSettings)
        });

        const data = await response.json();

        if (data.success) {
            currentSettings = newSettings;
            showToast('Configuración guardada correctamente', 'success');
            closeSettingsModal();

            // Si el monitoreo está activo, reiniciarlo con la nueva configuración
            if (isMonitoring) {
                showToast('Reinicia el monitoreo para aplicar los cambios', 'info');
            }
        } else {
            showToast(data.error || 'Error al guardar configuración', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('Error al guardar configuración', 'error');
    } finally {
        hideLoading(elements.saveSettingsBtn);
    }
}

// Render Functions
function renderEmails(emails) {
    if (!emails || emails.length === 0) {
        elements.emailsContainer.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-inbox"></i>
                <h3>No hay correos todavía</h3>
                <p>Haz clic en "Iniciar Monitoreo" o "Verificar Ahora" para buscar correos de Netflix</p>
            </div>
        `;
        return;
    }

    elements.emailsContainer.innerHTML = '';

    // Agregar cada email con un delay para animación escalonada
    emails.forEach((email, index) => {
        setTimeout(() => {
            const card = createEmailCard(email);
            elements.emailsContainer.appendChild(card);
        }, index * 100); // 100ms de delay entre cada tarjeta
    });
}

function createEmailCard(email) {
    const card = document.createElement('div');
    card.className = `email-card type-${email.type}`;

    const typeName = {
        'codigo_inicio': 'Código de Inicio',
        'codigo_temporal': 'Código Temporal',
        'actualizacion_hogar': 'Actualización Hogar'
    }[email.type] || 'Desconocido';

    card.innerHTML = `
        <div class="email-header">
            <div>
                <div class="email-subject">${escapeHtml(email.subject)}</div>
            </div>
            <div class="email-type-badge">${typeName}</div>
        </div>
        
        <div class="email-meta">
            <span>
                <i class="fas fa-user"></i>
                ${escapeHtml(email.from)}
            </span>
            <span>
                <i class="fas fa-envelope"></i>
                ${escapeHtml(email.account)}
            </span>
            <span>
                <i class="fas fa-clock"></i>
                ${formatDate(email.date)}
            </span>
        </div>
        
        ${email.code ? `
            <div class="email-code">
                <div>
                    <div class="code-label">Código extraído:</div>
                    <div class="code-value">${escapeHtml(email.code)}</div>
                </div>
                <button class="btn btn-icon" onclick="copyCode('${escapeHtml(email.code)}')" title="Copiar código">
                    <i class="fas fa-copy"></i>
                </button>
            </div>
        ` : ''}
        
        ${email.body_preview ? `
            <div class="email-preview">
                ${escapeHtml(email.body_preview)}...
            </div>
        ` : ''}
    `;

    return card;
}

function updateStats(emails) {
    const stats = {
        total: emails.length,
        codigo_inicio: 0,
        codigo_temporal: 0,
        actualizacion_hogar: 0
    };

    emails.forEach(email => {
        if (email.type in stats) {
            stats[email.type]++;
        }
    });

    animateValue(elements.totalEmails, parseInt(elements.totalEmails.textContent) || 0, stats.total);
    animateValue(elements.codigosInicio, parseInt(elements.codigosInicio.textContent) || 0, stats.codigo_inicio);
    animateValue(elements.codigosTemporal, parseInt(elements.codigosTemporal.textContent) || 0, stats.codigo_temporal);
    animateValue(elements.actualizacionesHogar, parseInt(elements.actualizacionesHogar.textContent) || 0, stats.actualizacion_hogar);
}

// Filters
function applyFilters() {
    loadEmails();
}

// Modal
function openSettingsModal() {
    elements.settingsModal.classList.add('active');
}

function closeSettingsModal() {
    elements.settingsModal.classList.remove('active');
}

// Utility Functions
function copyCode(code) {
    navigator.clipboard.writeText(code).then(() => {
        showToast('Código copiado al portapapeles', 'success');
    }).catch(() => {
        showToast('Error al copiar código', 'error');
    });
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };

    toast.innerHTML = `
        <i class="fas ${icons[type]} toast-icon"></i>
        <div class="toast-message">${escapeHtml(message)}</div>
    `;

    elements.toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideInRight 0.3s ease-out reverse';
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 4000);
}

function showLoading(button) {
    button.disabled = true;
    button.dataset.originalHtml = button.innerHTML;
    button.innerHTML = '<span class="loading"></span>';
}

function hideLoading(button) {
    button.disabled = false;
    if (button.dataset.originalHtml) {
        button.innerHTML = button.dataset.originalHtml;
        delete button.dataset.originalHtml;
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateStr) {
    try {
        const date = new Date(dateStr);
        const now = new Date();
        const diff = now - date;

        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);

        if (days > 0) return `Hace ${days} día${days > 1 ? 's' : ''}`;
        if (hours > 0) return `Hace ${hours} hora${hours > 1 ? 's' : ''}`;
        if (minutes > 0) return `Hace ${minutes} minuto${minutes > 1 ? 's' : ''}`;
        return 'Hace un momento';
    } catch {
        return dateStr;
    }
}

function formatDateTime(isoString) {
    try {
        const date = new Date(isoString);
        return date.toLocaleString('es-ES', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    } catch {
        return isoString;
    }
}

function animateValue(element, start, end, duration = 500) {
    const range = end - start;
    const increment = range / (duration / 16);
    let current = start;

    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            current = end;
            clearInterval(timer);
        }
        element.textContent = Math.round(current);
    }, 16);
}

function playNotificationSound() {
    // Crear un beep simple usando Web Audio API
    try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);

        oscillator.frequency.value = 800;
        oscillator.type = 'sine';

        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);

        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.5);
    } catch (error) {
        console.log('No se pudo reproducir sonido de notificación');
    }
}

// Auto-load emails and stats on page load
setTimeout(() => {
    loadEmails();
}, 1000);
