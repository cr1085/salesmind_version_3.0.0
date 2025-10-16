#!/usr/bin/env python3
"""
Prueba simple y específica de idiomas
"""

import sys
sys.path.append('.')

from modules import create_app
from modules.models import Client

def test_simple_languages():
    """Prueba específica con 3 idiomas principales"""
    
    app = create_app()
    
    with app.app_context():
        client = Client.query.filter_by(name="Constructora Manatí").first()
        if not client:
            print("❌ Cliente no encontrado")
            return
        
        from modules.assistant.core import get_commercial_response
        
        # Pruebas específicas más simples
        tests = [
            ("🇪🇸", "¿Cuánto cuesta el Modelo Terra?"),
            ("🇺🇸", "What is the price of the Terra Model?"),
            ("🇫🇷", "Quel est le prix du Modèle Terra?")
        ]
        
        for flag, question in tests:
            print(f"\n{flag} Pregunta: {question}")
            try:
                response = get_commercial_response(question, client.public_id)
                print(f"✅ Respuesta: {response}")
            except Exception as e:
                print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_simple_languages()