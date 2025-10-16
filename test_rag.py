#!/usr/bin/env python3
"""
Script de prueba para verificar que el sistema RAG funciona correctamente
con el cliente 'Constructora Manatí'
"""

import os
import sys
sys.path.append('.')

from modules import create_app
from modules.models import Client

def test_rag_system():
    """Prueba el sistema RAG con el cliente Constructora Manatí"""
    
    app = create_app()
    
    with app.app_context():
        try:
            # Buscar el cliente Constructora Manatí
            client = Client.query.filter_by(name="Constructora Manatí").first()
            
            if not client:
                print("❌ Cliente 'Constructora Manatí' no encontrado")
                return False
                
            print(f"✅ Cliente encontrado: {client.name}")
            print(f"   🔑 Public ID: {client.public_id}")
            
            # Importar el sistema RAG
            from modules.assistant.core import get_commercial_response
            
            # Hacer una consulta de prueba
            test_query = "¿Qué modelos de casa tienen disponibles?"
            print(f"\n🔍 Consulta de prueba: {test_query}")
            
            result = get_commercial_response(test_query, client.public_id)
            
            print(f"\n✅ Respuesta recibida:")
            print(f"   📝 Texto: {result.get('response', 'Sin respuesta')[:200]}...")
            print(f"   📊 Chunks encontrados: {result.get('chunks_used', 0)}")
            print(f"   ⚡ Tiempo: {result.get('processing_time', 0):.2f}s")
            
            return True
            
        except Exception as e:
            print(f"❌ Error en prueba RAG: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    print("🚀 Probando sistema RAG con Constructora Manatí...")
    success = test_rag_system()
    
    if success:
        print("\n🎉 ¡Prueba exitosa! El sistema RAG funciona correctamente")
        print("📞 El agente está listo para atender consultas")
    else:
        print("\n❌ Falló la prueba. Revisar configuración.")
        sys.exit(1)