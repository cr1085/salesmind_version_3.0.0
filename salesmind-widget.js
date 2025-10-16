/**
 * 🚀 SALESMIND WIDGET - SISTEMA DE CHAT IA EMBEBIBLE
 * Integración sencilla para cualquier sitio web
 * 
 * INSTALACIÓN:
 * 1. Sube este archivo a tu servidor
 * 2. Agrega una línea al HTML del cliente:
 *    <script src="https://tu-servidor.com/salesmind-widget.js" data-client-id="TU_ID_CLIENTE"></script>
 */

(function() {
    'use strict';
    
    // 🔧 CONFIGURACIÓN AUTOMÁTICA
    const script = document.currentScript;
    const CLIENT_ID = script.getAttribute('data-client-id') || 'demo-client-123';
    const API_URL = script.getAttribute('data-api-url') || 'http://localhost:5000/chat-api';
    const WIDGET_TITLE = script.getAttribute('data-title') || 'Asistente IA';
    const WIDGET_SUBTITLE = script.getAttribute('data-subtitle') || 'Consultor Digital';
    
    // Variables globales del widget
    let isOpen = false;
    let isProcessing = false;
    let messageCount = 0;
    
    // 🎨 ESTILOS DEL WIDGET
    const CSS = `
        /* Widget Container */
        #salesmind-widget {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 999999;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        
        /* Botón flotante */
        #salesmind-trigger {
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #007bff, #0056b3);
            border-radius: 50%;
            border: none;
            cursor: pointer;
            box-shadow: 0 4px 20px rgba(0, 123, 255, 0.4);
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
            position: relative;
        }
        
        #salesmind-trigger:hover {
            transform: scale(1.1);
            box-shadow: 0 6px 25px rgba(0, 123, 255, 0.6);
        }
        
        #salesmind-trigger svg {
            width: 24px;
            height: 24px;
            fill: white;
        }
        
        /* Notification badge */
        #salesmind-badge {
            position: absolute;
            top: -5px;
            right: -5px;
            width: 20px;
            height: 20px;
            background: #ff4757;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: bold;
            color: white;
            display: none;
        }
        
        /* Ventana de chat */
        #salesmind-window {
            position: absolute;
            bottom: 80px;
            right: 0;
            width: 350px;
            height: 500px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
            display: none;
            flex-direction: column;
            overflow: hidden;
            animation: slideIn 0.3s ease-out;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(20px) scale(0.95);
            }
            to {
                opacity: 1;
                transform: translateY(0) scale(1);
            }
        }
        
        /* Header del chat */
        #salesmind-header {
            background: linear-gradient(135deg, #007bff, #0056b3);
            color: white;
            padding: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        #salesmind-header .avatar {
            width: 35px;
            height: 35px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        #salesmind-header .info h4 {
            margin: 0;
            font-size: 14px;
            font-weight: 600;
        }
        
        #salesmind-header .info p {
            margin: 0;
            font-size: 12px;
            opacity: 0.9;
        }
        
        #salesmind-close {
            margin-left: auto;
            background: none;
            border: none;
            color: white;
            cursor: pointer;
            padding: 5px;
            border-radius: 3px;
        }
        
        #salesmind-close:hover {
            background: rgba(255, 255, 255, 0.1);
        }
        
        /* Área de mensajes */
        #salesmind-messages {
            flex: 1;
            padding: 15px;
            overflow-y: auto;
            background: #f8f9fa;
        }
        
        #salesmind-messages::-webkit-scrollbar {
            width: 4px;
        }
        
        #salesmind-messages::-webkit-scrollbar-thumb {
            background: #ddd;
            border-radius: 2px;
        }
        
        .message {
            margin-bottom: 15px;
            animation: messageSlide 0.3s ease-out;
        }
        
        @keyframes messageSlide {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .user-message {
            text-align: right;
        }
        
        .user-message .content {
            display: inline-block !important;
            background: #007bff !important;
            color: white !important;
            padding: 10px 15px;
            border-radius: 15px 15px 5px 15px;
            max-width: 80%;
            font-size: 14px !important;
            line-height: 1.4 !important;
            visibility: visible !important;
            opacity: 1 !important;
        }
        
        .bot-message {
            display: flex;
            gap: 8px;
        }
        
        .bot-message .avatar {
            width: 30px;
            height: 30px;
            background: #007bff;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            margin-top: 5px;
        }
        
        .bot-message .avatar svg {
            width: 16px;
            height: 16px;
            fill: white;
        }
        
        .bot-message .content {
            background: white !important;
            border: 1px solid #e9ecef;
            padding: 10px 15px;
            border-radius: 15px 15px 15px 5px;
            max-width: 80%;
            font-size: 14px !important;
            line-height: 1.4 !important;
            color: #333 !important;
            display: block !important;
            visibility: visible !important;
            opacity: 1 !important;
        }
        
        .download-btn {
            background: #28a745;
            color: white;
            padding: 6px 12px;
            border: none;
            border-radius: 8px;
            font-size: 12px;
            margin: 5px 2px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
        }
        
        .download-btn:hover {
            background: #218838;
        }
        
        /* Input area */
        #salesmind-input-area {
            padding: 15px;
            background: white;
            border-top: 1px solid #e9ecef;
            display: flex;
            gap: 10px;
        }
        
        #salesmind-input {
            flex: 1;
            border: 1px solid #ddd;
            border-radius: 20px;
            padding: 10px 15px;
            outline: none;
            font-size: 14px;
        }
        
        #salesmind-input:focus {
            border-color: #007bff;
        }
        
        #salesmind-send {
            background: #007bff;
            color: white;
            border: none;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        #salesmind-send:hover {
            background: #0056b3;
        }
        
        #salesmind-send:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        .typing-indicator {
            display: none;
            padding: 10px 15px;
            font-style: italic;
            color: #666;
            font-size: 13px;
        }
        
        .spinner {
            width: 16px;
            height: 16px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-top: 2px solid white;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* Mobile responsive */
        @media (max-width: 480px) {
            #salesmind-window {
                width: 300px;
                height: 450px;
            }
        }
    `;
    
    // 📱 CREAR HTML DEL WIDGET
    function createWidget() {
        const widgetHTML = `
            <div id="salesmind-widget">
                <!-- Botón flotante -->
                <button id="salesmind-trigger">
                    <svg viewBox="0 0 24 24">
                        <path d="M12,2A2,2 0 0,1 14,4C14,4.74 13.6,5.39 13,5.73V7A1,1 0 0,0 14,8H20A2,2 0 0,1 22,10V16A2,2 0 0,1 20,18H16.5C16.5,18 16.5,18 16.5,18L12,22.5L7.5,18C7.5,18 7.5,18 7.5,18H4A2,2 0 0,1 2,16V10A2,2 0 0,1 4,8H10A1,1 0 0,0 11,7V5.73C10.4,5.39 10,4.74 10,4A2,2 0 0,1 12,2M7.5,13.5C7.5,14.4 8.1,15 9,15C9.9,15 10.5,14.4 10.5,13.5C10.5,12.6 9.9,12 9,12C8.1,12 7.5,12.6 7.5,13.5M13.5,13.5C13.5,14.4 14.1,15 15,15C15.9,15 16.5,14.4 16.5,13.5C16.5,12.6 15.9,12 15,12C14.1,12 13.5,12.6 13.5,13.5Z"/>
                    </svg>
                    <span id="salesmind-badge">1</span>
                </button>
                
                <!-- Ventana de chat -->
                <div id="salesmind-window">
                    <div id="salesmind-header">
                        <div class="avatar">
                            <svg viewBox="0 0 24 24">
                                <path d="M12,2A2,2 0 0,1 14,4C14,4.74 13.6,5.39 13,5.73V7A1,1 0 0,0 14,8H20A2,2 0 0,1 22,10V16A2,2 0 0,1 20,18H16.5L12,22.5L7.5,18H4A2,2 0 0,1 2,16V10A2,2 0 0,1 4,8H10A1,1 0 0,0 11,7V5.73C10.4,5.39 10,4.74 10,4A2,2 0 0,1 12,2Z"/>
                            </svg>
                        </div>
                        <div class="info">
                            <h4>${WIDGET_TITLE}</h4>
                            <p>${WIDGET_SUBTITLE}</p>
                        </div>
                        <button id="salesmind-close">✕</button>
                    </div>
                    
                    <div id="salesmind-messages"></div>
                    
                    <div class="typing-indicator" id="salesmind-typing">
                        El asistente está escribiendo...
                    </div>
                    
                    <div id="salesmind-input-area">
                        <input type="text" id="salesmind-input" placeholder="Escribe tu mensaje...">
                        <button id="salesmind-send">
                            <svg viewBox="0 0 24 24" width="16" height="16">
                                <path d="M2,21L23,12L2,3V10L17,12L2,14V21Z" fill="currentColor"/>
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        return widgetHTML;
    }
    
    // 💬 FUNCIONES DEL CHAT
    function addMessage(text, type) {
        const messagesContainer = document.getElementById('salesmind-messages');
        if (!messagesContainer) {
            console.error('❌ No se encontró el contenedor de mensajes');
            return;
        }
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        
        if (type === 'bot') {
            // Procesar enlaces de descarga
            const processedText = text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, 
                '<button class="download-btn" onclick="SalesMindWidget.downloadPDF(\'$2\', \'$1\')">📄 $1</button>'
            );
            
            messageDiv.innerHTML = `
                <div class="avatar">
                    <svg viewBox="0 0 24 24">
                        <path d="M12,2A2,2 0 0,1 14,4C14,4.74 13.6,5.39 13,5.73V7A1,1 0 0,0 14,8H20A2,2 0 0,1 22,10V16A2,2 0 0,1 20,18H16.5L12,22.5L7.5,18H4A2,2 0 0,1 2,16V10A2,2 0 0,1 4,8H10A1,1 0 0,0 11,7V5.73C10.4,5.39 10,4.74 10,4A2,2 0 0,1 12,2Z"/>
                    </svg>
                </div>
                <div class="content" style="color: #333 !important; font-size: 14px !important; line-height: 1.4 !important; display: block !important; visibility: visible !important; opacity: 1 !important; background: white !important; padding: 10px 15px; border-radius: 15px 15px 15px 5px; border: 1px solid #e9ecef;">${processedText}</div>
            `;
        } else {
            messageDiv.innerHTML = `<div class="content" style="color: #ffffff !important; font-size: 14px !important; line-height: 1.4 !important; display: inline-block !important; visibility: visible !important; opacity: 1 !important; background: #007bff !important; padding: 10px 15px; border-radius: 15px 15px 5px 15px;">${text}</div>`;
        }
        
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        // Debug para verificar que el texto se agregó
        console.log(`✅ Mensaje agregado (${type}):`, text.substring(0, 50) + '...');
        console.log('📋 HTML del mensaje:', messageDiv.outerHTML.substring(0, 200) + '...');
    }
    
    async function sendMessage() {
        const input = document.getElementById('salesmind-input');
        const sendBtn = document.getElementById('salesmind-send');
        const typing = document.getElementById('salesmind-typing');
        
        const message = input.value.trim();
        if (!message || isProcessing) return;
        
        isProcessing = true;
        messageCount++;
        
        // Agregar mensaje del usuario
        addMessage(message, 'user');
        input.value = '';
        
        // UI feedback
        sendBtn.disabled = true;
        sendBtn.innerHTML = '<div class="spinner"></div>';
        typing.style.display = 'block';
        
        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    clientId: CLIENT_ID
                })
            });
            
            const data = await response.json();
            
            // Simular tiempo de escritura
            setTimeout(() => {
                typing.style.display = 'none';
                
                if (data.reply) {
                    addMessage(data.reply, 'bot');
                } else {
                    addMessage('Lo siento, no pude procesar tu mensaje. Intenta de nuevo.', 'bot');
                }
                
                // Restaurar UI
                sendBtn.disabled = false;
                sendBtn.innerHTML = `
                    <svg viewBox="0 0 24 24" width="16" height="16">
                        <path d="M2,21L23,12L2,3V10L17,12L2,14V21Z" fill="currentColor"/>
                    </svg>
                `;
                isProcessing = false;
            }, 1500);
            
        } catch (error) {
            console.error('Error:', error);
            typing.style.display = 'none';
            addMessage('Error de conexión. Verifica tu internet e intenta nuevamente.', 'bot');
            
            sendBtn.disabled = false;
            sendBtn.innerHTML = `
                <svg viewBox="0 0 24 24" width="16" height="16">
                    <path d="M2,21L23,12L2,3V10L17,12L2,14V21Z" fill="currentColor"/>
                </svg>
            `;
            isProcessing = false;
        }
    }
    
    // 📥 FUNCIÓN DE DESCARGA
    function downloadPDF(url, fileName) {
        const link = document.createElement('a');
        link.href = url;
        link.download = fileName + '.pdf';
        link.target = '_blank';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
    
    // 🚀 INICIALIZACIÓN
    function init() {
        // Agregar CSS
        const style = document.createElement('style');
        style.textContent = CSS;
        document.head.appendChild(style);
        
        // Agregar HTML
        const widgetContainer = document.createElement('div');
        widgetContainer.innerHTML = createWidget();
        document.body.appendChild(widgetContainer);
        
        // Event listeners
        const trigger = document.getElementById('salesmind-trigger');
        const window = document.getElementById('salesmind-window');
        const close = document.getElementById('salesmind-close');
        const input = document.getElementById('salesmind-input');
        const send = document.getElementById('salesmind-send');
        
        trigger.addEventListener('click', () => {
            isOpen = !isOpen;
            window.style.display = isOpen ? 'flex' : 'none';
            
            if (isOpen && messageCount === 0) {
                // Mensaje de bienvenida
                setTimeout(() => {
                    addMessage(`¡Hola! Soy tu asistente IA. Estoy aquí para ayudarte con consultas, cotizaciones y información. ¿En qué puedo asistirte?`, 'bot');
                }, 500);
            }
            
            // Ocultar badge
            document.getElementById('salesmind-badge').style.display = 'none';
        });
        
        close.addEventListener('click', () => {
            isOpen = false;
            window.style.display = 'none';
        });
        
        send.addEventListener('click', sendMessage);
        
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
        
        // Mostrar badge inicial
        setTimeout(() => {
            document.getElementById('salesmind-badge').style.display = 'flex';
        }, 3000);
    }
    
    // Exponer funciones globales necesarias
    window.SalesMindWidget = {
        downloadPDF: downloadPDF
    };
    
    // Inicializar cuando el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
})();