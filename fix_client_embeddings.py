#!/usr/bin/env python
# fix_client_embeddings.py
import sys
import os
sys.path.append(os.path.dirname(__file__))

from modules import create_app, db
from modules.models import Client, Document, Embedding, FAISSIndex
from modules.vector_manager import VectorManager
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from config import Config
import numpy as np
import faiss
import pickle

def create_real_embeddings():
    app = create_app()
    with app.app_context():
        print("🔧 REPARANDO CLIENTE DEMO")
        print("=" * 50)
        
        # Buscar cliente
        client = Client.query.filter_by(public_id='demo-client-12345').first()
        if not client:
            print("❌ Cliente no encontrado")
            return False
        
        print(f"✅ Cliente encontrado: {client.name}")
        
        # Buscar documento
        document = Document.query.filter_by(client_id=client.id).first()
        if not document:
            print("❌ Documento no encontrado")
            return False
        
        print(f"✅ Documento encontrado: {document.filename}")
        
        # Eliminar embeddings existentes (si los hay)
        Embedding.query.filter_by(client_id=client.id).delete()
        FAISSIndex.query.filter_by(client_id=client.id).delete()
        db.session.commit()
        print("🧹 Embeddings anteriores eliminados")
        
        # Configurar modelo de embeddings
        if not Config.GOOGLE_API_KEY:
            print("❌ GOOGLE_API_KEY no configurada")
            return False
        
        embedding_model = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004",
            google_api_key=Config.GOOGLE_API_KEY
        )
        print("✅ Modelo de embeddings configurado")
        
        # Dividir texto en chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, 
            chunk_overlap=200
        )
        
        text_chunks = text_splitter.split_text(document.extracted_text)
        print(f"✅ Texto dividido en {len(text_chunks)} chunks")
        
        # Generar embeddings reales
        print("🔄 Generando embeddings reales...")
        embeddings_list = []
        
        for i, chunk in enumerate(text_chunks):
            print(f"   Procesando chunk {i+1}/{len(text_chunks)}")
            
            try:
                # Generar embedding real con Google
                embedding_vector = embedding_model.embed_query(chunk)
                embedding_array = np.array(embedding_vector, dtype=np.float32)
                
                # Guardar en base de datos
                embedding_record = Embedding(
                    client_id=client.id,
                    document_id=document.id,
                    text_chunk=chunk,
                    chunk_index=i,
                    embedding_vector=pickle.dumps(embedding_array),
                    vector_dimension=len(embedding_vector),
                    model_used='text-embedding-004'
                )
                
                db.session.add(embedding_record)
                embeddings_list.append(embedding_array)
                
            except Exception as e:
                print(f"❌ Error en chunk {i}: {e}")
                return False
        
        db.session.commit()
        print(f"✅ {len(embeddings_list)} embeddings guardados")
        
        # Crear índice FAISS
        print("🔄 Creando índice FAISS...")
        dimension = len(embeddings_list[0])
        index = faiss.IndexFlatL2(dimension)
        
        # Convertir a array y agregar al índice
        vectors_array = np.array(embeddings_list)
        index.add(vectors_array)
        
        # Serializar índice
        index_bytes = faiss.serialize_index(index)
        
        # Guardar en base de datos
        faiss_record = FAISSIndex(
            client_id=client.id,
            index_name='main_index',
            index_data=index_bytes,
            vector_dimension=dimension,
            total_vectors=index.ntotal,
            index_type='IndexFlatL2',
            is_active=True,
            version=1
        )
        
        db.session.add(faiss_record)
        db.session.commit()
        
        print(f"✅ Índice FAISS creado con {index.ntotal} vectores")
        print("🎉 CLIENTE DEMO REPARADO Y LISTO!")
        return True

if __name__ == "__main__":
    success = create_real_embeddings()
    if success:
        print("\n🌟 SISTEMA COMPLETAMENTE FUNCIONAL")
        print("📝 Ahora puedes probar:")
        print("   - ¿Cuánto cuesta una casa?")
        print("   - Dame una cotización")
        print("   - What's the price of an apartment?")
        print("\n🔗 Abre: http://127.0.0.1:5000/pagina_cliente_ejemplo.html")
    else:
        print("\n❌ Error configurando embeddings")