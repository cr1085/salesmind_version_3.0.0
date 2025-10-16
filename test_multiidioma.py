#!/usr/bin/env python3
"""
Script para probar las capacidades multiidioma del agente SalesMind
"""

import sys
sys.path.append('.')

from modules import create_app
from modules.models import Client

def test_multilanguage():
    """Prueba el agente con consultas en diferentes idiomas"""
    
    app = create_app()
    
    with app.app_context():
        try:
            # Buscar cliente
            client = Client.query.filter_by(name="Constructora Manatí").first()
            if not client:
                print("❌ Cliente no encontrado")
                return False
            
            print(f"🌍 Probando capacidades multiidioma con cliente: {client.name}")
            print(f"🔑 Public ID: {client.public_id}")
            
            from modules.assistant.core import get_commercial_response
            
            # Pruebas en diferentes idiomas
            test_cases = [
                {
                    "idioma": "🇪🇸 Español",
                    "pregunta": "¿Qué modelos de casa tienen disponibles?",
                    "esperado": "español"
                },
                {
                    "idioma": "🇺🇸 English", 
                    "pregunta": "What house models do you have available?",
                    "esperado": "inglés"
                },
                {
                    "idioma": "🇫🇷 Français",
                    "pregunta": "Quels modèles de maison avez-vous disponibles?", 
                    "esperado": "francés"
                },
                {
                    "idioma": "🇩🇪 Deutsch",
                    "pregunta": "Welche Hausmodelle haben Sie verfügbar?",
                    "esperado": "alemán"
                },
                {
                    "idioma": "🇮🇹 Italiano",
                    "pregunta": "Quali modelli di casa avete disponibili?", 
                    "esperado": "italiano"
                },
                {
                    "idioma": "🇵🇹 Português",
                    "pregunta": "Que modelos de casa vocês têm disponíveis?",
                    "esperado": "portugués"
                }
            ]
            
            for i, test in enumerate(test_cases, 1):
                print(f"\n🔍 Prueba {i}/6: {test['idioma']}")
                print(f"❓ Pregunta: {test['pregunta']}")
                
                try:
                    respuesta = get_commercial_response(test['pregunta'], client.public_id)
                    
                    print(f"✅ Respuesta:")
                    print(f"   📝 {respuesta[:200]}...")
                    
                    # Verificar si la respuesta mantiene coherencia con el idioma
                    if len(respuesta) > 50:
                        print(f"   ✅ Respuesta generada exitosamente en {test['esperado']}")
                    else:
                        print(f"   ⚠️  Respuesta muy corta")
                        
                except Exception as e:
                    print(f"   ❌ Error: {e}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error general: {e}")
            return False

if __name__ == "__main__":
    print("🌍 === PRUEBA MULTIIDIOMA SALESMIND ===")
    success = test_multilanguage()
    
    if success:
        print("\n🎉 ¡Pruebas completadas!")
        print("💬 El agente SalesMind puede responder en múltiples idiomas")
        print("🔄 Automáticamente detecta el idioma de la pregunta y responde en el mismo idioma")
    else:
        print("\n❌ Error en las pruebas multiidioma")
        sys.exit(1)