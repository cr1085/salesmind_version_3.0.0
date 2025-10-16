# modules/integrations/extension_hooks.py
"""
SISTEMA DE HOOKS PARA EXTENSIONES SEGURAS
=========================================

Este sistema permite que las extensiones se conecten al core SIN modificar código existente.
Usa el patrón Observer para que las extensiones escuchen eventos del sistema.

EVENTOS DISPONIBLES:
- client_created         -> Cuando se crea un cliente
- document_uploaded      -> Cuando se sube un documento  
- embeddings_created     -> Cuando se crean embeddings
- faiss_index_updated    -> Cuando se actualiza índice FAISS
- chat_message_received  -> Cuando llega un mensaje de chat
- quote_generated        -> Cuando se genera una cotización
- response_sent          -> Cuando se envía respuesta al usuario

EXTENSIONES PUEDEN:
- Escuchar eventos
- Procesar datos adicionales
- Agregar funcionalidades
- Generar reportes
- Integrar con APIs externas

EXTENSIONES NO PUEDEN:
- Modificar flujo principal
- Romper funcionalidad existente
- Interferir con otros módulos
"""

import threading
from typing import Dict, List, Callable, Any
from datetime import datetime

class SafeHookSystem:
    """Sistema de hooks thread-safe para extensiones."""
    
    def __init__(self):
        self._hooks: Dict[str, List[Callable]] = {}
        self._lock = threading.Lock()
    
    def register_hook(self, event_name: str, callback: Callable):
        """Registra un hook para un evento específico."""
        with self._lock:
            if event_name not in self._hooks:
                self._hooks[event_name] = []
            self._hooks[event_name].append(callback)
            print(f"✅ Hook registrado para evento '{event_name}'")
    
    def emit_event(self, event_name: str, data: Any = None):
        """Emite un evento a todas las extensiones registradas."""
        with self._lock:
            callbacks = self._hooks.get(event_name, [])
        
        # Ejecutar callbacks de forma segura
        for callback in callbacks:
            try:
                # Ejecutar en thread separado para no bloquear el core
                thread = threading.Thread(
                    target=self._safe_callback_execution,
                    args=(callback, event_name, data)
                )
                thread.daemon = True  # No bloquea el cierre del programa
                thread.start()
            except Exception as e:
                print(f"⚠️ Error en hook {event_name}: {e}")
                # IMPORTANTE: Los errores en extensiones NO afectan el sistema core
    
    def _safe_callback_execution(self, callback: Callable, event_name: str, data: Any):
        """Ejecuta un callback de forma segura, aislando errores."""
        try:
            callback(data)
        except Exception as e:
            print(f"❌ Error en extensión para evento '{event_name}': {e}")
            # Log error pero NO propagarlo al sistema core
    
    def list_hooks(self) -> Dict[str, int]:
        """Lista todos los hooks registrados."""
        with self._lock:
            return {event: len(callbacks) for event, callbacks in self._hooks.items()}

# Instancia global del sistema de hooks
hook_system = SafeHookSystem()

# Funciones de conveniencia para emitir eventos desde el core
def emit_client_created(client_data):
    """Emite evento cuando se crea un cliente."""
    hook_system.emit_event('client_created', client_data)

def emit_document_uploaded(document_data):
    """Emite evento cuando se sube un documento."""
    hook_system.emit_event('document_uploaded', document_data)

def emit_embeddings_created(embeddings_data):
    """Emite evento cuando se crean embeddings.""" 
    hook_system.emit_event('embeddings_created', embeddings_data)

def emit_faiss_index_updated(index_data):
    """Emite evento cuando se actualiza índice FAISS."""
    hook_system.emit_event('faiss_index_updated', index_data)

def emit_chat_message_received(message_data):
    """Emite evento cuando llega mensaje de chat."""
    hook_system.emit_event('chat_message_received', message_data)

def emit_quote_generated(quote_data):
    """Emite evento cuando se genera cotización."""
    hook_system.emit_event('quote_generated', quote_data)

def emit_response_sent(response_data):
    """Emite evento cuando se envía respuesta."""
    hook_system.emit_event('response_sent', response_data)