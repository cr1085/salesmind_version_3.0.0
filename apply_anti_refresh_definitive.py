#!/usr/bin/env python
# apply_anti_refresh_definitive.py - APLICAR CORRECCIONES DEFINITIVAS
"""
🛡️ APLICADOR DE CORRECCIONES ANTI-REFRESH DEFINITIVAS
====================================================

Aplica todas las correcciones necesarias para eliminar completamente
el problema de refresh de página y pérdida de conversación.
"""

import os
import shutil
from datetime import datetime

def apply_definitive_fix():
    """Aplica correcciones definitivas anti-refresh."""
    
    print("🛡️ APLICADOR DE CORRECCIONES ANTI-REFRESH DEFINITIVAS")
    print("=" * 70)
    
    original_file = "pagina_cliente_ejemplo.html"
    backup_dir = "backups"
    
    # 1. Crear directorio de backups
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # 2. Backup con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"{backup_dir}/pagina_cliente_ejemplo_{timestamp}.html"
    
    if os.path.exists(original_file):
        shutil.copy2(original_file, backup_file)
        print(f"✅ Backup creado: {backup_file}")
    
    # 3. Leer archivo original
    with open(original_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"\n🔧 APLICANDO CORRECCIONES DEFINITIVAS:")
    
    # CORRECCIÓN 1: Agregar indicador de estado
    print("   🔧 1. Agregando indicador de estado visual")
    head_end = "</head>"
    status_indicator = """    <style>
        #status-indicator {
            position: fixed; top: 10px; right: 10px; 
            padding: 5px 10px; border-radius: 5px; 
            font-size: 12px; z-index: 10000;
            background: #28a745; color: white;
            font-family: monospace;
        }
    </style>
</head>"""
    
    if head_end in content and "#status-indicator" not in content:
        content = content.replace(head_end, status_indicator)
        print("      ✅ Indicador de estado agregado")
    
    # CORRECCIÓN 2: Agregar indicador al body
    body_start = '<body>'
    indicator_html = '''<body>
    
    <!-- 🛡️ INDICADOR ANTI-REFRESH -->
    <div id="status-indicator">🛡️ ANTI-REFRESH ACTIVO</div>'''
    
    if body_start in content and "status-indicator" not in content:
        content = content.replace(body_start, indicator_html)
        print("      ✅ Indicador HTML agregado")
    
    # CORRECCIÓN 3: Mejorar función sendMessage con protección total
    old_send_function = '''const sendMessage = async () => {
            const messageText = chatInput.value.trim();
            if (messageText === '') return;
            console.log('📤 Enviando mensaje:', messageText); // ✅ LOGGING
            appendMessage(messageText, 'user-message');
            chatInput.value = '';
            chatInput.disabled = true;
            sendButton.disabled = true;

            try {
                const response = await fetch(`${API_HOST}/chat-api`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: messageText, clientId: CLIENT_PUBLIC_ID })
                });
                if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
                const data = await response.json();
                appendMessage(data.reply, 'bot-message');
            } catch (error) {
                console.error('Error:', error);
                appendMessage('Lo siento, hubo un problema de conexión.', 'bot-message');
            } finally {
                chatInput.disabled = false;
                sendButton.disabled = false;
                chatInput.focus();
            }
        };'''
    
    new_send_function = '''const sendMessage = async (e) => {
            try {
                // 🛡️ PREVENCIÓN TOTAL DE NAVEGACIÓN
                if (e) {
                    e.preventDefault();
                    e.stopPropagation();
                    e.stopImmediatePropagation();
                }
                
                const messageText = chatInput.value.trim();
                if (messageText === '') return;
                
                console.log('📤 Enviando mensaje:', messageText);
                
                // 🛡️ ACTUALIZAR INDICADOR
                const statusIndicator = document.getElementById('status-indicator');
                if (statusIndicator) {
                    statusIndicator.textContent = '🔄 ENVIANDO...';
                    statusIndicator.style.background = '#ffc107';
                }
                
                appendMessage(messageText, 'user-message');
                chatInput.value = '';
                chatInput.disabled = true;
                sendButton.disabled = true;

                // 🛡️ FETCH CON PROTECCIÓN ANTI-REDIRECT
                const response = await fetch(`${API_HOST}/chat-api`, {
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json',
                        'Cache-Control': 'no-cache'
                    },
                    body: JSON.stringify({ message: messageText, clientId: CLIENT_PUBLIC_ID }),
                    redirect: 'error' // 🛡️ NO seguir redirecciones
                });
                
                if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
                const data = await response.json();
                appendMessage(data.reply, 'bot-message');
                
                // 🛡️ RESTAURAR INDICADOR
                if (statusIndicator) {
                    statusIndicator.textContent = '✅ ENVIADO';
                    statusIndicator.style.background = '#28a745';
                }
                
            } catch (error) {
                console.error('❌ Error completo:', error);
                appendMessage('Lo siento, hubo un problema de conexión.', 'bot-message');
                
                const statusIndicator = document.getElementById('status-indicator');
                if (statusIndicator) {
                    statusIndicator.textContent = '❌ ERROR';
                    statusIndicator.style.background = '#dc3545';
                }
            } finally {
                chatInput.disabled = false;
                sendButton.disabled = false;
                chatInput.focus();
                
                // 🛡️ RESTAURAR INDICADOR DESPUÉS DE 2 SEG
                setTimeout(() => {
                    const statusIndicator = document.getElementById('status-indicator');
                    if (statusIndicator) {
                        statusIndicator.textContent = '🛡️ ANTI-REFRESH ACTIVO';
                        statusIndicator.style.background = '#28a745';
                    }
                }, 2000);
            }
        };'''
    
    if old_send_function in content:
        content = content.replace(old_send_function, new_send_function)
        print("      ✅ Función sendMessage mejorada con protección total")
    
    # CORRECCIÓN 4: Agregar protecciones globales al final del script
    old_script_end = '''    </script>
    </body>
</html>'''
    
    new_script_end = '''        
        // 🛡️ PROTECCIONES GLOBALES ANTI-REFRESH
        
        // Capturar TODOS los errores
        window.addEventListener('error', (e) => {
            console.error('💥 ERROR GLOBAL:', e.error);
            const statusIndicator = document.getElementById('status-indicator');
            if (statusIndicator) {
                statusIndicator.textContent = '⚠️ ERROR DETECTADO';
                statusIndicator.style.background = '#dc3545';
            }
        });
        
        // Capturar promesas rechazadas
        window.addEventListener('unhandledrejection', (e) => {
            console.error('💥 PROMISE REJECTION:', e.reason);
            e.preventDefault(); // 🛡️ Prevenir navegación por error
        });
        
        // 🛡️ PREVENIR SUBMIT GLOBAL
        document.addEventListener('submit', (e) => {
            console.log('🚫 SUBMIT DETECTADO Y CANCELADO');
            e.preventDefault();
            e.stopPropagation();
            e.stopImmediatePropagation();
        });
        
        // 🛡️ TRIPLE PROTECCIÓN KEYDOWN
        chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                e.stopPropagation();
                e.stopImmediatePropagation();
            }
        });
        
        console.log('🛡️ PROTECCIONES ANTI-REFRESH ACTIVAS');
        
    </script>
    </body>
</html>'''
    
    if old_script_end in content:
        content = content.replace(old_script_end, new_script_end)
        print("      ✅ Protecciones globales agregadas")
    
    # CORRECCIÓN 5: Mejorar enlaces de descarga
    old_link_replace = '''const htmlText = text.replace(/\\[([^\\]]+)\\]\\(([^)]+)\\)/g, '<a href="$2" download style="color: #FFD700; text-decoration: underline;" target="_blank" onclick="event.preventDefault(); event.stopPropagation(); window.open(this.href, \\'_blank\\');">$1</a>');'''
    
    new_link_replace = '''const htmlText = text.replace(/\\[([^\\]]+)\\]\\(([^)]+)\\)/g, (match, linkText, url) => {
                    return `<span style="color: #FFD700; text-decoration: underline; cursor: pointer; padding: 5px; background: rgba(255,215,0,0.1); border-radius: 3px;" onclick="handleSafeDownload('${url}', '${linkText}')">${linkText}</span>`;
                });
                
                // 🛡️ FUNCIÓN DE DESCARGA SEGURA
                window.handleSafeDownload = function(url, filename) {
                    try {
                        console.log('📥 Descarga segura:', url);
                        const tempLink = document.createElement('a');
                        tempLink.style.display = 'none';
                        tempLink.href = url;
                        tempLink.download = filename || '';
                        tempLink.target = '_blank';
                        tempLink.rel = 'noopener noreferrer';
                        document.body.appendChild(tempLink);
                        tempLink.click();
                        document.body.removeChild(tempLink);
                        
                        const statusIndicator = document.getElementById('status-indicator');
                        if (statusIndicator) {
                            statusIndicator.textContent = '📥 DESCARGANDO';
                            statusIndicator.style.background = '#17a2b8';
                            setTimeout(() => {
                                statusIndicator.textContent = '🛡️ ANTI-REFRESH ACTIVO';
                                statusIndicator.style.background = '#28a745';
                            }, 2000);
                        }
                    } catch (error) {
                        console.error('❌ Error descarga:', error);
                        window.open(url, '_blank', 'noopener,noreferrer');
                    }
                };'''
    
    if old_link_replace in content:
        content = content.replace(old_link_replace, new_link_replace)
        print("      ✅ Sistema de descarga segura implementado")
    
    # 6. Guardar archivo corregido
    with open(original_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n💾 ARCHIVO CORREGIDO GUARDADO: {original_file}")
    
    print(f"\n📋 RESUMEN DE CORRECCIONES APLICADAS:")
    print(f"   🛡️ Indicador visual de estado")
    print(f"   🛡️ Función sendMessage ultra-protegida") 
    print(f"   🛡️ Captura global de errores")
    print(f"   🛡️ Prevención de submit automático")
    print(f"   🛡️ Triple protección en eventos Enter")
    print(f"   🛡️ Sistema de descarga segura")
    print(f"   🛡️ Protección anti-redirect en fetch")
    
    print(f"\n🧪 INSTRUCCIONES DE PRUEBA:")
    print(f"   1. Actualizar página con Ctrl+F5 (hard refresh)")
    print(f"   2. Verificar indicador '🛡️ ANTI-REFRESH ACTIVO' en esquina")
    print(f"   3. Enviar mensaje con Enter - NO debe refrescar")
    print(f"   4. Solicitar cotización - NO debe refrescar")
    print(f"   5. Hacer click en PDF - NO debe refrescar")
    
    print(f"\n🔍 DEBUG:")
    print(f"   - Abrir DevTools (F12) → Console")
    print(f"   - Buscar mensajes: '🛡️ PROTECCIONES ANTI-REFRESH ACTIVAS'")
    print(f"   - Verificar que NO aparezca: 'Navigated to...'")
    
    return True

if __name__ == "__main__":
    apply_definitive_fix()