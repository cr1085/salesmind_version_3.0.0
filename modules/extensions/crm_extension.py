# modules/extensions/crm_extension.py
"""
EXTENSIÓN CRM - EJEMPLO DE FUNCIONALIDAD AVANZADA SIN TOCAR CORE
===============================================================

Esta extensión agrega funcionalidades de CRM SIN modificar código existente.

FUNCIONALIDADES NUEVAS:
- Gestión de leads automática
- Seguimiento de interacciones
- Scoring de clientes potenciales
- Automatización de email marketing
- Pipeline de ventas
- Reportes de conversión

ARQUITECTURA SEGURA:
- Usa hooks del sistema para escuchar eventos
- Almacena datos en tablas separadas
- Procesa en background threads
- NO interfiere con operaciones core
- Puede activarse/desactivarse sin afectar el sistema
"""

from ..extensions import BaseExtension, register_extension
from ..integrations.extension_hooks import hook_system
from ..models import Client, Conversation
from .. import db
from datetime import datetime
from typing import Dict, List, Optional
import threading

class CRMExtension(BaseExtension):
    """Extensión CRM que opera independientemente del core."""
    
    def __init__(self):
        super().__init__("crm")
        self.version = "1.0.0" 
        self.description = "Sistema CRM integrado"
        self.lead_scoring_enabled = True
        self.email_automation_enabled = False  # Desactivado por defecto
    
    def initialize(self):
        """Inicializa CRM sin tocar código existente."""
        # Registrar hooks para eventos relevantes
        hook_system.register_hook('chat_message_received', self._process_lead_interaction)
        hook_system.register_hook('quote_generated', self._handle_quote_request)
        hook_system.register_hook('client_created', self._setup_crm_profile)
        print(f"✅ CRM Extension v{self.version} inicializada")
    
    def _process_lead_interaction(self, message_data):
        """Procesa interacciones para scoring de leads."""
        try:
            if not self.lead_scoring_enabled:
                return
            
            # Extraer información del mensaje
            client_id = message_data.get('client_id')
            message_text = message_data.get('message', '')
            
            # Calcular score basado en intención
            intent_score = self._calculate_intent_score(message_text)
            
            # Actualizar perfil CRM del lead
            self._update_lead_score(client_id, intent_score)
            
        except Exception as e:
            print(f"⚠️ Error procesando lead: {e}")
            # Error no se propaga al sistema principal
    
    def _handle_quote_request(self, quote_data):
        """Maneja solicitudes de cotización para pipeline de ventas."""
        try:
            client_id = quote_data.get('client_id')
            quote_amount = quote_data.get('total_amount', 0)
            
            # Marcar como oportunidad calificada
            self._mark_as_qualified_opportunity(client_id, quote_amount)
            
            # Programar seguimiento automático
            self._schedule_follow_up(client_id)
            
        except Exception as e:
            print(f"⚠️ Error en pipeline de ventas: {e}")
    
    def _setup_crm_profile(self, client_data):
        """Configura perfil CRM para nuevo cliente."""
        try:
            client_id = client_data.get('id')
            # Inicializar perfil CRM sin afectar tabla de clientes principal
            self._create_crm_profile(client_id)
        except Exception as e:
            print(f"⚠️ Error configurando CRM: {e}")
    
    def _calculate_intent_score(self, message: str) -> int:
        """Calcula score de intención de compra."""
        # Palabras que indican alta intención
        high_intent_words = [
            'comprar', 'buy', 'purchase', 'cotización', 'quote', 'precio', 'price',
            'cuando', 'when', 'disponible', 'available', 'financiamiento', 'financing'
        ]
        
        # Palabras que indican baja intención  
        low_intent_words = [
            'información', 'info', 'curious', 'maybe', 'thinking', 'considering'
        ]
        
        message_lower = message.lower()
        
        high_matches = sum(1 for word in high_intent_words if word in message_lower)
        low_matches = sum(1 for word in low_intent_words if word in message_lower)
        
        # Score de 1 a 100
        base_score = 50
        score = base_score + (high_matches * 15) - (low_matches * 10)
        
        return max(1, min(100, score))
    
    def _update_lead_score(self, client_id: int, intent_score: int):
        """Actualiza score del lead en sistema CRM separado."""
        # En implementación real, esto escribiría a tabla CRM separada
        print(f"📊 Lead Score actualizado - Cliente {client_id}: {intent_score}/100")
    
    def _mark_as_qualified_opportunity(self, client_id: int, amount: float):
        """Marca como oportunidad calificada en pipeline."""
        # En implementación real, esto movería el lead al pipeline de ventas
        print(f"🎯 Oportunidad calificada - Cliente {client_id}: ${amount:,.2f}")
    
    def _schedule_follow_up(self, client_id: int):
        """Programa seguimiento automático."""
        # En implementación real, esto programaría emails o notificaciones
        print(f"📅 Seguimiento programado para Cliente {client_id}")
    
    def _create_crm_profile(self, client_id: int):
        """Crea perfil CRM inicial."""
        # En implementación real, esto crearía registro en tabla CRM separada
        print(f"👤 Perfil CRM creado para Cliente {client_id}")
    
    def get_lead_pipeline(self) -> List[Dict]:
        """Obtiene pipeline de leads actual."""
        try:
            # En implementación real, consultaría tabla CRM
            # Por ahora devolvemos datos simulados
            return [
                {
                    'client_id': 1,
                    'stage': 'qualified',
                    'score': 85,
                    'potential_value': 150000,
                    'last_interaction': datetime.now()
                }
            ]
        except Exception as e:
            print(f"❌ Error obteniendo pipeline: {e}")
            return []
    
    def get_client_crm_data(self, client_id: int) -> Dict:
        """Obtiene datos CRM de un cliente específico."""
        try:
            # En implementación real, consultaría perfil CRM completo
            return {
                'lead_score': 75,
                'stage': 'prospect',
                'interactions': 5,
                'last_contact': datetime.now(),
                'potential_value': 85000,
                'notes': 'Cliente interesado en propiedades comerciales'
            }
        except Exception as e:
            print(f"❌ Error obteniendo datos CRM: {e}")
            return {}

# Configuración de la extensión
def configure_crm_extension():
    """Configura la extensión CRM según necesidades."""
    crm = register_extension('crm', CRMExtension)
    
    # Configuraciones opcionales
    # crm.lead_scoring_enabled = True
    # crm.email_automation_enabled = False
    
    return crm

# Registrar automáticamente
configure_crm_extension()