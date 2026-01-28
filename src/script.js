// Configuración global
const SUPABASE_URL = localStorage.getItem('supabase_url') || 'https://grytlszzjoqfhpmxgptx.supabase.co';
const SUPABASE_KEY = localStorage.getItem('supabase_key') || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdyeXRsc3p6am9xZmhwbXhncHR4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk1MjM3MDYsImV4cCI6MjA4NTA5OTcwNn0.k6TFapvUyMImQIX73T2mxjSyAm2FYmgFEaD6BCIE4Ks';
const GITHUB_TOKEN = localStorage.getItem('extraccion_token') || '';

// Estado global
let currentFilter = 'all';
let isLoading = false;
let refreshInterval;

// Puntos de extracción configurados
const PUNTOS_CONFIG = {
    brisas: { 
        name: 'Brisas', 
        script: 'telegram_brisas_pdf.py',
        group_id: '-4797788824',
        valores_adicionales: [
            { nombre: 'TELEVISION', valor: 25000, comision: 0 }
        ]
    },
    tortuga: { 
        name: 'Tortuga', 
        script: 'telegram_tortuga_pdf.py',
        group_id: '-4639790763',
        valores_adicionales: [
            { nombre: 'CLIENTE CONDUCTOR', valor: 40000, comision: 5000 }
        ]
    },
    cano_pescado: { 
        name: 'Cano Pescado', 
        script: 'telegram_cano_pescado_pdf.py',
        group_id: '-4930938311',
        valores_adicionales: [
            { nombre: 'CLIENTE', valor: 45000, comision: 5000 },
            { nombre: 'TELEVISION', valor: 25000, comision: 0 }
        ]
    },
    cerritos: { 
        name: 'Cerritos', 
        script: 'telegram_cerritos_pdf.py',
        group_id: '-1000000000', // Reemplazar con ID real
        valores_adicionales: []
    },
    manantiales_1: { 
        name: 'Manantiales 1', 
        script: 'telegram_manantiales_1_pdf.py',
        group_id: '-1000000000', // Reemplazar con ID real
        valores_adicionales: []
    },
    manantiales_2: { 
        name: 'Manantiales 2', 
        script: 'telegram_manantiales_2_pdf.py',
        group_id: '-1000000000', // Reemplazar con ID real
        valores_adicionales: []
    },
    miravalle: { 
        name: 'Miravalle', 
        script: 'telegram_miravalle_pdf.py',
        group_id: '-1000000000', // Reemplazar con ID real
        valores_adicionales: []
    },
    san_miguel: { 
        name: 'San Miguel', 
        script: 'telegram_san_miguel_pdf.py',
        group_id: '-1000000000', // Reemplazar con ID real
        valores_adicionales: []
    },
    cachicamo: { 
        name: 'Cachicamo', 
        script: 'telegram_cachicamo_pdf.py',
        group_id: '-1000000000', // Reemplazar con ID real
        valores_adicionales: []
    },
    cano_lajas: { 
        name: 'Cano Lajas', 
        script: 'telegram_cano_lajas_pdf.py',
        group_id: '-1000000000', // Reemplazar con ID real
        valores_adicionales: []
    },
    tropezon: { 
        name: 'Tropezon', 
        script: 'telegram_tropezon_pdf.py',
        group_id: '-1000000000', // Reemplazar con ID real
        valores_adicionales: []
    }
};

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    setupEventListeners();
    setDefaultDates();
    checkSupabaseConnection();
    loadHistory();
    updateStatus();
    startAutoRefresh();
}

function setupEventListeners() {
    // Botones principales
    document.getElementById('extractAllBtn').addEventListener('click', extractAll);
    document.getElementById('extractSelectedBtn').addEventListener('click', extractSelected);
    document.getElementById('loadMoreBtn').addEventListener('click', loadMoreHistory);
    
    // Modal
    document.getElementById('modalClose').addEventListener('click', closeModal);
    document.getElementById('detailsModal').addEventListener('click', function(e) {
        if (e.target === this) closeModal();
    });
    
    // Filtros
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            setActiveFilter(this.dataset.filter);
        });
    });
    
    // Selección de puntos
    document.querySelectorAll('.punto-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', updateSelectedCount);
    });
}

function setDefaultDates() {
    const today = new Date();
    const lastWeek = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
    
    document.getElementById('startDate').value = lastWeek.toISOString().split('T')[0];
    document.getElementById('endDate').value = today.toISOString().split('T')[0];
}

async function checkSupabaseConnection() {
    if (SUPABASE_URL === 'YOUR_SUPABASE_URL') {
        showToast('Configura las credenciales de Supabase para continuar', 'warning');
        showConfigModal();
        return false;
    }
    
    try {
        const response = await fetch(`${SUPABASE_URL}/rest/v1/extracciones?limit=1`, {
            headers: {
                'apikey': SUPABASE_KEY,
                'Authorization': `Bearer ${SUPABASE_KEY}`
            }
        });
        return response.ok;
    } catch (error) {
        console.error('Error conectando a Supabase:', error);
        showToast('Error conectando a la base de datos', 'error');
        return false;
    }
}

function showConfigModal() {
    const modal = document.createElement('div');
    modal.className = 'modal show';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3><i class="fas fa-cog"></i> Configuración de Supabase</h3>
                <button class="modal-close">&times;</button>
            </div>
            <div class="modal-body">
                <div class="config-form">
                    <div class="form-group">
                        <label for="supabaseUrl">URL de Supabase:</label>
                        <input type="text" id="supabaseUrlInput" placeholder="https://xxx.supabase.co" value="${SUPABASE_URL}">
                    </div>
                    <div class="form-group">
                        <label for="supabaseKey">API Key (anon public):</label>
                        <input type="password" id="supabaseKeyInput" placeholder="eyJhbGciOi..." value="${SUPABASE_KEY}">
                    </div>
                    <button class="btn btn-primary" onclick="saveSupabaseConfig()">Guardar Configuración</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    modal.querySelector('.modal-close').addEventListener('click', () => {
        document.body.removeChild(modal);
    });
}

function saveSupabaseConfig() {
    const url = document.getElementById('supabaseUrlInput').value.trim();
    const key = document.getElementById('supabaseKeyInput').value.trim();
    
    if (!url || !key) {
        showToast('Completa todos los campos', 'error');
        return;
    }
    
    localStorage.setItem('supabase_url', url);
    localStorage.setItem('supabase_key', key);
    
    // Recargar la página para aplicar cambios
    window.location.reload();
}

// Funciones de extracción
async function extractAll() {
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    
    if (!validateDates(startDate, endDate)) return;
    
    const puntos = Object.keys(PUNTOS_CONFIG);
    await triggerExtraction('masiva', puntos, startDate, endDate);
}

async function extractSelected() {
    const selectedPuntos = Array.from(document.querySelectorAll('.punto-checkbox:checked'))
        .map(cb => cb.value);
    
    if (selectedPuntos.length === 0) {
        showToast('Selecciona al menos un punto para extraer', 'warning');
        return;
    }
    
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    
    if (!validateDates(startDate, endDate)) return;
    
    await triggerExtraction('individual', selectedPuntos, startDate, endDate);
}

function validateDates(startDate, endDate) {
    if (!startDate || !endDate) {
        showToast('Selecciona un rango de fechas válido', 'error');
        return false;
    }
    
    const start = new Date(startDate);
    const end = new Date(endDate);
    
    if (start > end) {
        showToast('La fecha de inicio debe ser anterior a la fecha fin', 'error');
        return false;
    }
    
    return true;
}

async function triggerExtraction(tipo, puntos, startDate, endDate) {
    setProcessingState(true);
    
    // Crear registro en la base de datos
    const extraccionData = {
        tipo: tipo,
        puntos: puntos.join(','),
        fecha_inicio: startDate,
        fecha_fin: endDate,
        estado: 'procesando',
        creado_at: new Date().toISOString()
    };
    
    try {
        const response = await fetch(`${SUPABASE_URL}/rest/v1/extracciones`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'apikey': SUPABASE_KEY,
                'Authorization': `Bearer ${SUPABASE_KEY}`,
                'Prefer': 'return=representation'
            },
            body: JSON.stringify(extraccionData)
        });
        
        if (!response.ok) throw new Error('Error creando extracción');
        
        const [extraccion] = await response.json();
        
        // Disparar GitHub Action
        await triggerGitHubAction(extraccion.id, puntos, startDate, endDate);
        
        showToast(`Extracción ${tipo} iniciada correctamente`, 'success');
        loadHistory();
        
    } catch (error) {
        console.error('Error en extracción:', error);
        showToast('Error iniciando extracción', 'error');
    } finally {
        setProcessingState(false);
    }
}

async function triggerGitHubAction(extraccionId, puntos, startDate, endDate) {
    // En un entorno real, esto llamaría a una API para disparar el GitHub Action
    // Por ahora, simulamos el trigger
    
    const webhookUrl = 'https://api.github.com/repos/YOUR_USERNAME/extraccion-datos-web/dispatches';
    
    try {
        // Esto requiere un token de GitHub con permisos de workflows
        const response = await fetch(webhookUrl, {
            method: 'POST',
            headers: {
                'Authorization': `token YOUR_GITHUB_TOKEN`,
                'Content-Type': 'application/json',
                'Accept': 'application/vnd.github.v3+json'
            },
            body: JSON.stringify({
                event_type: 'extraction_triggered',
                client_payload: {
                    extraccion_id: extraccionId,
                    puntos: puntos,
                    start_date: startDate,
                    end_date: endDate
                }
            })
        });
        
        // Para desarrollo, mostramos solo log
        console.log('GitHub Action triggered:', { extraccionId, puntos, startDate, endDate });
        
    } catch (error) {
        console.error('Error disparando GitHub Action:', error);
        // En desarrollo, simulamos que se disparó
    }
}

function setProcessingState(processing) {
    isLoading = processing;
    const btn = document.getElementById('extractAllBtn');
    const statusIndicator = document.getElementById('statusIndicator');
    const statusDot = statusIndicator.querySelector('.status-dot');
    const statusText = statusIndicator.querySelector('.status-text');
    
    if (processing) {
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Procesando...';
        statusDot.classList.add('processing');
        statusText.textContent = 'Procesando';
    } else {
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-play"></i> Extraer Todos los Puntos';
        statusDot.classList.remove('processing');
        statusText.textContent = 'Listo';
    }
}

// Funciones de historial
async function loadHistory() {
    try {
        const response = await fetch(`${SUPABASE_URL}/rest/v1/extracciones?order=creado_at.desc&limit=20`, {
            headers: {
                'apikey': SUPABASE_KEY,
                'Authorization': `Bearer ${SUPABASE_KEY}`
            }
        });
        
        if (!response.ok) throw new Error('Error cargando historial');
        
        const extracciones = await response.json();
        displayHistory(extracciones);
        
    } catch (error) {
        console.error('Error cargando historial:', error);
        displayHistory([]);
    }
}

function displayHistory(extracciones) {
    const historyList = document.getElementById('historyList');
    
    if (extracciones.length === 0) {
        historyList.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-inbox"></i>
                <p>No hay extracciones registradas</p>
            </div>
        `;
        return;
    }
    
    const filteredExtracciones = filterExtracciones(extracciones, currentFilter);
    
    historyList.innerHTML = filteredExtracciones.map(extraccion => {
        const typeIcon = extraccion.tipo === 'masiva' ? 'fa-globe' : 'fa-map-marker-alt';
        const statusClass = getStatusClass(extraccion.estado);
        
        return `
            <div class="history-item ${extraccion.estado}" onclick="showDetails(${extraccion.id})">
                <div class="history-item-header">
                    <div class="history-item-type">
                        <i class="fas ${typeIcon}"></i>
                        ${extraccion.tipo.toUpperCase()} - ${extraccion.puntos}
                    </div>
                    <div class="history-item-status ${statusClass}">
                        ${extraccion.estado}
                    </div>
                </div>
                <div class="history-item-details">
                    <div><i class="fas fa-calendar"></i> ${formatDate(extraccion.fecha_inicio)} - ${formatDate(extraccion.fecha_fin)}</div>
                    <div><i class="fas fa-clock"></i> ${formatDateTime(extraccion.creado_at)}</div>
                    ${extraccion.total_enviar ? `<div><i class="fas fa-dollar-sign"></i> Total: $${extraccion.total_enviar.toLocaleString()}</div>` : ''}
                </div>
            </div>
        `;
    }).join('');
}

function filterExtracciones(extracciones, filter) {
    switch (filter) {
        case 'masiva':
            return extracciones.filter(e => e.tipo === 'masiva');
        case 'individual':
            return extracciones.filter(e => e.tipo === 'individual');
        case 'completadas':
            return extracciones.filter(e => e.estado === 'completada');
        case 'error':
            return extracciones.filter(e => e.estado === 'error');
        default:
            return extracciones;
    }
}

function setActiveFilter(filter) {
    currentFilter = filter;
    
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.filter === filter);
    });
    
    loadHistory();
}

// Funciones de estado
async function updateStatus() {
    try {
        const today = new Date().toISOString().split('T')[0];
        
        // Última extracción
        const lastResponse = await fetch(`${SUPABASE_URL}/rest/v1/extracciones?order=creado_at.desc&limit=1`, {
            headers: {
                'apikey': SUPABASE_KEY,
                'Authorization': `Bearer ${SUPABASE_KEY}`
            }
        });
        
        // Extracciones hoy
        const todayResponse = await fetch(`${SUPABASE_URL}/rest/v1/extracciones?creado_at=gte.${today}&count=exact`, {
            headers: {
                'apikey': SUPABASE_KEY,
                'Authorization': `Bearer ${SUPABASE_KEY}`,
                'Prefer': 'count=exact'
            }
        });
        
        if (lastResponse.ok) {
            const last = await lastResponse.json();
            document.getElementById('lastExtraction').textContent = 
                last.length > 0 ? formatDateTime(last[0].creado_at) : 'No realizada';
        }
        
        if (todayResponse.ok) {
            const count = todayResponse.headers.get('content-range')?.split('/')[1] || 0;
            document.getElementById('todayExtractions').textContent = count;
        }
        
    } catch (error) {
        console.error('Error actualizando estado:', error);
    }
}

// Funciones de UI
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icon = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    }[type];
    
    toast.innerHTML = `
        <i class="fas ${icon}"></i>
        <span>${message}</span>
    `;
    
    toastContainer.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease forwards';
        setTimeout(() => {
            if (toastContainer.contains(toast)) {
                toastContainer.removeChild(toast);
            }
        }, 300);
    }, 3000);
}

async function showDetails(extraccionId) {
    try {
        // Cargar detalles de la extracción
        const response = await fetch(`${SUPABASE_URL}/rest/v1/extracciones?id=eq.${extraccionId}`, {
            headers: {
                'apikey': SUPABASE_KEY,
                'Authorization': `Bearer ${SUPABASE_KEY}`
            }
        });
        
        if (!response.ok) throw new Error('Error cargando detalles');
        
        const [extraccion] = await response.json();
        
        // Cargar historial de mensajes
        const historyResponse = await fetch(`${SUPABASE_URL}/rest/v1/historial?extraccion_id=eq.${extraccionId}&order=creado_at.desc`, {
            headers: {
                'apikey': SUPABASE_KEY,
                'Authorization': `Bearer ${SUPABASE_KEY}`
            }
        });
        
        const mensajes = historyResponse.ok ? await historyResponse.json() : [];
        
        // Mostrar modal con detalles
        const modal = document.getElementById('detailsModal');
        const modalBody = document.getElementById('modalBody');
        
        modalBody.innerHTML = `
            <div class="extraction-details">
                <div class="detail-section">
                    <h4><i class="fas fa-info-circle"></i> Información General</h4>
                    <p><strong>Tipo:</strong> ${extraccion.tipo}</p>
                    <p><strong>Puntos:</strong> ${extraccion.puntos}</p>
                    <p><strong>Periodo:</strong> ${formatDate(extraccion.fecha_inicio)} - ${formatDate(extraccion.fecha_fin)}</p>
                    <p><strong>Estado:</strong> <span class="status-badge ${getStatusClass(extraccion.estado)}">${extraccion.estado}</span></p>
                    <p><strong>Creado:</strong> ${formatDateTime(extraccion.creado_at)}</p>
                    ${extraccion.completado_at ? `<p><strong>Completado:</strong> ${formatDateTime(extraccion.completado_at)}</p>` : ''}
                </div>
                
                ${extraccion.total_ventas !== null ? `
                <div class="detail-section">
                    <h4><i class="fas fa-chart-line"></i> Resultados</h4>
                    <p><strong>Total Ventas:</strong> $${extraccion.total_ventas?.toLocaleString() || 'N/A'}</p>
                    <p><strong>Total Comisiones:</strong> $${extraccion.total_comision?.toLocaleString() || 'N/A'}</p>
                    <p><strong>Comisión Alcanza:</strong> $${extraccion.comision_alcanza?.toLocaleString() || 'N/A'}</p>
                    <p><strong>Total a Enviar:</strong> $${extraccion.total_enviar?.toLocaleString() || 'N/A'}</p>
                </div>
                ` : ''}
                
                ${mensajes.length > 0 ? `
                <div class="detail-section">
                    <h4><i class="fas fa-history"></i> Registro de Eventos</h4>
                    <div class="messages-list">
                        ${mensajes.map(msg => `
                            <div class="message-item ${msg.tipo}">
                                <small>${formatDateTime(msg.creado_at)}</small>
                                <p>${msg.mensaje}</p>
                            </div>
                        `).join('')}
                    </div>
                </div>
                ` : ''}
            </div>
        `;
        
        modal.classList.add('show');
        
    } catch (error) {
        console.error('Error mostrando detalles:', error);
        showToast('Error cargando detalles', 'error');
    }
}

function closeModal() {
    document.getElementById('detailsModal').classList.remove('show');
}

// Funciones utilitarias
function getStatusClass(estado) {
    const classes = {
        'completada': 'status-completada',
        'procesando': 'status-procesando',
        'error': 'status-error'
    };
    return classes[estado] || 'status-procesando';
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-CO');
}

function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('es-CO', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function updateSelectedCount() {
    const selected = document.querySelectorAll('.punto-checkbox:checked').length;
    const btn = document.getElementById('extractSelectedBtn');
    
    if (selected > 0) {
        btn.innerHTML = `<i class="fas fa-download"></i> Extraer Seleccionados (${selected})`;
    } else {
        btn.innerHTML = '<i class="fas fa-download"></i> Extraer Seleccionados';
    }
}

function loadMoreHistory() {
    // Implementar paginación
    showToast('Cargar más históricos - implementación pendiente', 'info');
}

function startAutoRefresh() {
    // Actualizar cada 30 segundos
    refreshInterval = setInterval(() => {
        if (!isLoading) {
            updateStatus();
            loadHistory();
        }
    }, 30000);
}

// Limpiar al cerrar
window.addEventListener('beforeunload', () => {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
});