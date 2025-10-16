#!/usr/bin/env python
# test_quote_system.py
import requests
import json

def test_multilanguage_and_quotes():
    """Prueba las funcionalidades multilenguaje y de cotización"""
    
    API_URL = "http://127.0.0.1:5000/chat-api"
    CLIENT_ID = "demo-client-12345"
    
    print("🧪 PRUEBAS DEL SISTEMA SALESMIND")
    print("="*50)
    
    # Prueba 1: Español con cotización
    print("\n1️⃣ PRUEBA EN ESPAÑOL - COTIZACIÓN")
    data = {
        "message": "Hola, me interesa una casa. ¿Cuánto cuesta la casa moderna?",
        "clientId": CLIENT_ID
    }
    
    try:
        response = requests.post(API_URL, json=data)
        if response.status_code == 200:
            result = response.json()
            print("✅ Respuesta:", result["reply"][:200] + "...")
            if "PDF" in result["reply"] or "cotización" in result["reply"].lower():
                print("🎯 ¡COTIZACIÓN DETECTADA EN LA RESPUESTA!")
            else:
                print("⚠️ No se detectó cotización")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    # Prueba 2: Inglés
    print("\n2️⃣ PRUEBA EN INGLÉS")
    data = {
        "message": "Hello, I want to buy a house. How much does the modern house cost?",
        "clientId": CLIENT_ID
    }
    
    try:
        response = requests.post(API_URL, json=data)
        if response.status_code == 200:
            result = response.json()
            print("✅ Respuesta:", result["reply"][:200] + "...")
            # Verificar si responde en inglés
            if any(word in result["reply"].lower() for word in ["hello", "house", "price", "cost", "$"]):
                print("🎯 ¡RESPUESTA EN INGLÉS DETECTADA!")
            else:
                print("⚠️ Podría no estar respondiendo en inglés")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    # Prueba 3: Cotización explícita
    print("\n3️⃣ PRUEBA DE COTIZACIÓN EXPLÍCITA")
    data = {
        "message": "Por favor genera una cotización para el apartamento ejecutivo",
        "clientId": CLIENT_ID
    }
    
    try:
        response = requests.post(API_URL, json=data)
        if response.status_code == 200:
            result = response.json()
            print("✅ Respuesta:", result["reply"][:300] + "...")
            if "PDF" in result["reply"] or "download" in result["reply"].lower():
                print("🎯 ¡ENLACE DE DESCARGA PDF GENERADO!")
            else:
                print("⚠️ No se generó enlace de descarga")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    print("\n" + "="*50)
    print("🏁 PRUEBAS COMPLETADAS")

if __name__ == "__main__":
    test_multilanguage_and_quotes()