#!/usr/bin/env python3
"""
Prueba directa del endpoint web para verificar multiidioma
"""

import requests
import json
import time

def test_web_endpoint():
    """Prueba el endpoint web con diferentes idiomas"""
    
    # URL del endpoint
    url = "http://127.0.0.1:5000/chat-api"
    
    # ID del cliente Constructora Manatí
    client_id = "6068752e-3b84-400c-bd9c-1201fe1a0128"
    
    # Pruebas en diferentes idiomas
    tests = [
        {
            "language": "🇪🇸 Español",
            "message": "¿Cuánto cuesta el Modelo Terra?"
        },
        {
            "language": "🇺🇸 English", 
            "message": "What is the price of the Terra Model?"
        },
        {
            "language": "🇫🇷 Français",
            "message": "Quel est le prix du Modèle Terra?"
        }
    ]
    
    print("🌐 === PRUEBA DEL ENDPOINT WEB MULTIIDIOMA ===\n")
    
    for i, test in enumerate(tests, 1):
        print(f"🔍 Prueba {i}/3: {test['language']}")
        print(f"❓ Mensaje: {test['message']}")
        
        # Datos del request
        data = {
            "message": test["message"],
            "clientId": client_id
        }
        
        try:
            # Hacer request al endpoint
            response = requests.post(
                url, 
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                reply = result.get('reply', 'Sin respuesta')
                print(f"✅ Respuesta: {reply}")
                print(f"   📊 Status: {response.status_code}")
            else:
                print(f"❌ Error HTTP: {response.status_code}")
                print(f"   📝 Respuesta: {response.text}")
                
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
        
        print("-" * 60)
        time.sleep(2)  # Pausa entre requests

if __name__ == "__main__":
    print("⏱️ Esperando que el servidor se inicie...")
    time.sleep(5)
    test_web_endpoint()