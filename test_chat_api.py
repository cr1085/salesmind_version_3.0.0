#!/usr/bin/env python
# test_chat_api.py
import requests
import json
import sys

def test_chat_api():
    print("🧪 PROBANDO API DE CHAT")
    print("=" * 50)
    
    # Configuración
    api_url = "http://127.0.0.1:5000/chat-api"
    client_id = "demo-client-12345"
    
    # Mensaje de prueba
    test_message = "¿Cuánto cuesta una casa?"
    
    # Datos para enviar
    payload = {
        "message": test_message,
        "clientId": client_id
    }
    
    print(f"📤 Enviando mensaje: '{test_message}'")
    print(f"🆔 Cliente ID: {client_id}")
    print(f"🌐 URL: {api_url}")
    print()
    
    try:
        # Enviar petición
        response = requests.post(
            api_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        print()
        
        if response.status_code == 200:
            data = response.json()
            print("✅ RESPUESTA EXITOSA:")
            print(f"💬 Reply: {data.get('reply', 'No reply')}")
            print(f"⏰ Timestamp: {data.get('timestamp', 'No timestamp')}")
            print(f"👤 Client: {data.get('client_name', 'No client name')}")
            
        else:
            print("❌ ERROR EN LA RESPUESTA:")
            print(f"📄 Texto: {response.text}")
            
            try:
                error_data = response.json()
                print(f"🔍 Error JSON: {json.dumps(error_data, indent=2)}")
            except:
                print("📄 No es JSON válido")
        
    except requests.exceptions.ConnectionError:
        print("❌ ERROR DE CONEXIÓN:")
        print("   - Verifica que el servidor Flask esté ejecutándose")
        print("   - URL: http://127.0.0.1:5000")
        
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT:")
        print("   - El servidor no respondió en 30 segundos")
        
    except Exception as e:
        print(f"❌ ERROR INESPERADO: {str(e)}")
        import traceback
        traceback.print_exc()

def test_client_exists():
    print("\n🔍 VERIFICANDO CLIENTE EN BASE DE DATOS")
    print("=" * 50)
    
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(__file__))
        
        from modules import create_app, db
        from modules.models import Client, Document, Embedding, FAISSIndex
        
        app = create_app()
        with app.app_context():
            # Buscar cliente
            client = Client.query.filter_by(public_id='demo-client-12345').first()
            
            if client:
                print(f"✅ Cliente encontrado:")
                print(f"   - Nombre: {client.name}")
                print(f"   - ID: {client.id}")
                print(f"   - Public ID: {client.public_id}")
                
                # Verificar documentos
                docs = Document.query.filter_by(client_id=client.id).all()
                print(f"   - Documentos: {len(docs)}")
                
                # Verificar embeddings
                embeddings = Embedding.query.filter_by(client_id=client.id).all()
                print(f"   - Embeddings: {len(embeddings)}")
                
                # Verificar índices FAISS
                indexes = FAISSIndex.query.filter_by(client_id=client.id, is_active=True).all()
                print(f"   - Índices FAISS activos: {len(indexes)}")
                
                for idx in indexes:
                    print(f"     * {idx.index_name}: {idx.total_vectors} vectores")
                
                return True
            else:
                print("❌ Cliente no encontrado en la base de datos")
                return False
                
    except Exception as e:
        print(f"❌ Error verificando cliente: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Verificar cliente primero
    client_exists = test_client_exists()
    
    if client_exists:
        # Probar API
        test_chat_api()
    else:
        print("\n⚠️  Necesitas crear el cliente primero")
        print("   Ejecuta: python create_test_client.py")