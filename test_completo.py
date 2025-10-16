#!/usr/bin/env python3
"""
Prueba completa del agente SalesMind con PostgreSQL
"""

import os
import sys
sys.path.append('.')

def test_simple():
    """Prueba simple sin importar Flask"""
    try:
        # Probar conexión a PostgreSQL
        from modules.models import Client, Document, Embedding, FAISSIndex
        from modules import create_app
        
        app = create_app()
        
        with app.app_context():
            print("🔍 === VERIFICANDO BASE DE DATOS ===")
            
            # 1. Verificar cliente
            client = Client.query.filter_by(name="Constructora Manatí").first()
            if not client:
                print("❌ Cliente 'Constructora Manatí' no encontrado")
                return False
            
            print(f"✅ Cliente: {client.name}")
            print(f"   ID: {client.id}")
            print(f"   Public ID: {client.public_id}")
            
            # 2. Verificar documentos
            docs = Document.query.filter_by(client_id=client.id).all()
            print(f"✅ Documentos: {len(docs)}")
            for doc in docs:
                print(f"   - {doc.filename}: {len(doc.extracted_text)} caracteres")
            
            # 3. Verificar embeddings
            embeddings = Embedding.query.filter_by(client_id=client.id).all()
            print(f"✅ Embeddings: {len(embeddings)}")
            
            # 4. Verificar índice FAISS
            faiss_indices = FAISSIndex.query.filter_by(client_id=client.id).all()
            print(f"✅ Índices FAISS: {len(faiss_indices)}")
            
            if len(docs) == 0 or len(embeddings) == 0 or len(faiss_indices) == 0:
                print("❌ Faltan datos para el cliente")
                return False
            
            print("\n🧪 === PROBANDO SISTEMA RAG ===")
            
            # 5. Probar VectorManager directamente
            from modules.vector_manager import VectorManager
            
            vm = VectorManager()
            
            # Cargar índice FAISS
            print("📂 Cargando índice FAISS...")
            faiss_data = vm.load_faiss_index_for_client(client.id)
            
            if not faiss_data:
                print("❌ No se pudo cargar índice FAISS")
                return False
                
            index, embeddings_list = faiss_data
            print(f"✅ Índice FAISS cargado: {index.ntotal} vectores")
            
            # 6. Buscar chunks similares
            print("\n🔍 Buscando chunks similares...")
            question = "¿Qué modelos de casa tienen?"
            similar_chunks = vm.search_similar_chunks(client.id, question, top_k=2)
            
            print(f"✅ Chunks encontrados: {len(similar_chunks)}")
            for i, chunk in enumerate(similar_chunks):
                print(f"   {i+1}. {chunk['text'][:100]}...")
                print(f"      Campos: {list(chunk.keys())}")
                if 'similarity' in chunk:
                    print(f"      Similitud: {chunk['similarity']:.3f}")
                elif 'score' in chunk:
                    print(f"      Score: {chunk['score']:.3f}")
            
            return len(similar_chunks) > 0
            
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoint():
    """Prueba el endpoint de API"""
    try:
        print("\n🌐 === PROBANDO ENDPOINT API ===")
        
        from modules.assistant.core import get_commercial_response
        from modules import create_app
        
        app = create_app()
        
        with app.app_context():
            # Usar el public_id del cliente Constructora Manatí
            public_id = "6068752e-3b84-400c-bd9c-1201fe1a0128"
            question = "¿Qué modelos de casa ofrecen?"
            
            print(f"🔍 Pregunta: {question}")
            print(f"👤 Cliente: {public_id}")
            
            response = get_commercial_response(question, public_id)
            
            print(f"✅ Respuesta recibida: {len(response)} caracteres")
            print(f"📝 Respuesta: {response[:200]}...")
            
            return len(response) > 50  # Respuesta razonable
        
    except Exception as e:
        print(f"❌ Error en API: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 === PRUEBA COMPLETA DEL AGENTE SALESMIND ===\n")
    
    # Prueba 1: Base de datos y VectorManager
    success1 = test_simple()
    
    if success1:
        print("\n✅ Prueba 1 exitosa: Base de datos y vectores OK")
        
        # Prueba 2: API endpoint
        success2 = test_api_endpoint()
        
        if success2:
            print("\n🎉 ¡TODAS LAS PRUEBAS EXITOSAS!")
            print("🟢 El agente está funcionando correctamente con PostgreSQL")
            print("🔗 Puedes iniciar el servidor con: python app.py")
        else:
            print("\n❌ Falló prueba de API")
    else:
        print("\n❌ Falló prueba de base de datos")
        
    print(f"\nResultado final: {'✅ ÉXITO' if success1 and success2 else '❌ ERROR'}")