# modules/extensions/analytics_extension.py
"""
EXTENSIÓN DE ANALÍTICAS - EJEMPLO DE ESCALABILIDAD SEGURA
=========================================================

Esta extensión demuestra cómo agregar nuevas funciones SIN tocar código existente.

FUNCIONALIDADES QUE AGREGA:
- Estadísticas de uso por cliente
- Análisis de consultas más frecuentes  
- Reportes de rendimiento
- Métricas de satisfacción
- Dashboard de analíticas

INTEGRACIÓN SEGURA:
- Escucha eventos del sistema core
- Procesa datos en paralelo
- Almacena métricas en tablas separadas
- NO modifica flujo principal
- NO puede romper funcionalidad existente
"""

from ..extensions import BaseExtension, register_extension
from ..integrations.extension_hooks import hook_system
from ..models import Client, Conversation, QueryLog
from .. import db
import json
from datetime import datetime, timedelta
from collections import Counter
from typing import Dict, List

class AnalyticsExtension(BaseExtension):
    """Extensión de analíticas que se ejecuta de forma independiente."""
    
    def __init__(self):
        super().__init__("analytics")
        self.version = "1.0.0"
        self.description = "Sistema de analíticas y métricas"
    
    def initialize(self):
        """Inicializa la extensión registrando hooks."""
        # Escuchar eventos del sistema sin modificar código core
        hook_system.register_hook('chat_message_received', self._on_chat_message)
        hook_system.register_hook('client_created', self._on_client_created)
        hook_system.register_hook('quote_generated', self._on_quote_generated)
        print(f"✅ Extensión {self.name} inicializada")
    
    def _on_chat_message(self, message_data):
        """Procesa métricas cuando llega un mensaje de chat."""
        try:
            # Analizar patrones de uso
            self._update_usage_stats(message_data)
            self._analyze_query_patterns(message_data)
        except Exception as e:
            print(f"⚠️ Error en analíticas de chat: {e}")
    
    def _on_client_created(self, client_data):
        """Procesa métricas cuando se crea un cliente."""
        try:
            # Inicializar métricas del cliente
            self._initialize_client_metrics(client_data)
        except Exception as e:
            print(f"⚠️ Error en analíticas de cliente: {e}")
    
    def _on_quote_generated(self, quote_data):
        """Procesa métricas cuando se genera una cotización."""
        try:
            # Analizar conversiones
            self._track_conversion_metrics(quote_data)
        except Exception as e:
            print(f"⚠️ Error en analíticas de cotización: {e}")
    
    def _update_usage_stats(self, message_data):
        """Actualiza estadísticas de uso (implementación ejemplo)."""
        # Esta función podría escribir a una tabla separada de métricas
        pass
    
    def _analyze_query_patterns(self, message_data):
        """Analiza patrones de consultas (implementación ejemplo)."""
        # Esta función podría analizar tipos de preguntas más comunes
        pass
    
    def _initialize_client_metrics(self, client_data):
        """Inicializa métricas para nuevo cliente (implementación ejemplo)."""
        # Esta función podría crear perfil de analíticas del cliente
        pass
    
    def _track_conversion_metrics(self, quote_data):
        """Rastrea métricas de conversión (implementación ejemplo)."""
        # Esta función podría medir tasa de conversión de cotizaciones
        pass
    
    def get_client_analytics(self, client_id: int) -> Dict:
        """Obtiene analíticas de un cliente específico."""
        try:
            # Consultar datos sin afectar tablas core
            conversations = Conversation.query.filter_by(client_id=client_id).all()
            query_logs = QueryLog.query.filter_by(client_id=client_id).all()
            
            return {
                'total_conversations': len(conversations),
                'total_queries': len(query_logs),
                'avg_response_time': sum(q.response_time or 0 for q in query_logs) / len(query_logs) if query_logs else 0,
                'most_common_queries': self._get_common_queries(query_logs),
                'usage_trend': self._get_usage_trend(conversations)
            }
        except Exception as e:
            print(f"❌ Error obteniendo analíticas: {e}")
            return {}
    
    def _get_common_queries(self, query_logs: List) -> List:
        """Analiza consultas más comunes."""
        queries = [q.question.lower() for q in query_logs if q.question]
        counter = Counter(queries)
        return counter.most_common(5)
    
    def _get_usage_trend(self, conversations: List) -> Dict:
        """Calcula tendencia de uso."""
        if not conversations:
            return {}
        
        # Agrupar por fecha
        dates = [c.timestamp.date() for c in conversations]
        date_counter = Counter(dates)
        
        return {
            'daily_usage': dict(date_counter),
            'peak_day': max(date_counter.items(), key=lambda x: x[1]) if date_counter else None
        }

# Registrar la extensión automáticamente
register_extension('analytics', AnalyticsExtension)