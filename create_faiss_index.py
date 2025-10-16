#!/usr/bin/env python
# create_faiss_index.py
import sys
import os
sys.path.append(os.path.dirname(__file__))

from modules import create_app, db
from modules.models import Client, Document, Embedding, FAISSIndex
from modules.vector_manager import VectorManager
import numpy as np
import faiss
import pickle

def create_faiss_index_for_client():
    app = create_app()
    with app.app_context():
        # Buscar el cliente de prueba
        client = Client.query.filter_by(public_id='demo-client-12345').first()
        if not client:
            print("❌ Cliente demo no encontrado")
            return False
        
        print(f"🔍 Procesando cliente: {client.name} (ID: {client.id})")
        
        # Buscar embeddings existentes
        embeddings = Embedding.query.filter_by(client_id=client.id).all()
        
        if not embeddings:
            print("❌ No hay embeddings para este cliente")
            return False
        
        print(f"📊 Encontrados {len(embeddings)} embeddings")
        
        # Crear índice FAISS
        dimension = embeddings[0].vector_dimension
        index = faiss.IndexFlatL2(dimension)
        
        # Agregar vectores al índice
        vectors = []
        for embedding in embeddings:
            vector = pickle.loads(embedding.embedding_vector)
            vectors.append(vector)
        
        vectors_array = np.array(vectors).astype('float32')
        index.add(vectors_array)
        
        print(f"✅ Índice FAISS creado con {index.ntotal} vectores")
        
        # Serializar y guardar índice en PostgreSQL
        index_bytes = faiss.serialize_index(index)
        
        # Eliminar índice existente si existe
        existing_index = FAISSIndex.query.filter_by(
            client_id=client.id, 
            index_name='main_index',
            is_active=True
        ).first()
        
        if existing_index:
            existing_index.is_active = False
        
        # Crear nuevo índice
        faiss_index_record = FAISSIndex(
            client_id=client.id,
            index_name='main_index',
            index_data=index_bytes,
            vector_dimension=dimension,
            total_vectors=index.ntotal,
            index_type='IndexFlatL2',
            is_active=True,
            version=1
        )
        
        db.session.add(faiss_index_record)
        db.session.commit()
        
        print(f"✅ Índice guardado en PostgreSQL")
        print(f"🎉 Cliente listo para responder consultas!")
        return True

if __name__ == '__main__':
    success = create_faiss_index_for_client()
    if success:
        print("\n🌟 SISTEMA LISTO PARA COTIZACIONES")
        print("📝 Prueba preguntas como:")
        print("   - ¿Cuánto cuesta una casa?")
        print("   - Dame una cotización de apartamento")
        print("   - What's the price of a house?")
        print("   - Quanto custa uma casa?")
    else:
        print("\n❌ Error configurando el sistema")