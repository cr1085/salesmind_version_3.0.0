#!/usr/bin/env python
# auto_fix_clients.py - Arregla automáticamente cualquier cliente sin embeddings
import sys
import os
sys.path.append(os.path.dirname(__file__))

from modules import create_app, db
from modules.models import Client, Document, Embedding, FAISSIndex
from modules.vector_manager import VectorManager

def auto_fix_all_clients():
    """
    Encuentra y repara automáticamente todos los clientes que no tienen embeddings o índices.
    """
    app = create_app()
    with app.app_context():
        print("🔧 AUTO-REPARACIÓN DE CLIENTES")
        print("=" * 50)
        
        # Encontrar todos los clientes
        all_clients = Client.query.all()
        print(f"📊 Total de clientes: {len(all_clients)}")
        
        clients_fixed = 0
        vector_manager = VectorManager()
        
        for client in all_clients:
            print(f"\n🔍 Verificando cliente: {client.name} (ID: {client.id})")
            
            # Verificar si tiene documentos
            documents = Document.query.filter_by(client_id=client.id).all()
            print(f"   📄 Documentos: {len(documents)}")
            
            if not documents:
                print(f"   ⚠️ Sin documentos - saltando")
                continue
            
            # Verificar si tiene embeddings
            embeddings = Embedding.query.filter_by(client_id=client.id).all()
            print(f"   🧮 Embeddings: {len(embeddings)}")
            
            # Verificar si tiene índice FAISS activo
            faiss_indexes = FAISSIndex.query.filter_by(client_id=client.id, is_active=True).all()
            print(f"   🔧 Índices FAISS: {len(faiss_indexes)}")
            
            needs_repair = False
            
            # Si no tiene embeddings, los necesita
            if not embeddings:
                print(f"   ❌ Cliente necesita embeddings")
                needs_repair = True
                
                # Crear embeddings para todos los documentos
                for document in documents:
                    if document.extracted_text:
                        print(f"      🔄 Creando embeddings para: {document.filename}")
                        doc_embeddings = vector_manager.create_embeddings_from_document(document.id)
                        print(f"      ✅ {len(doc_embeddings)} embeddings creados")
                    else:
                        print(f"      ⚠️ Documento sin texto: {document.filename}")
            
            # Si no tiene índice FAISS activo, lo necesita
            if not faiss_indexes:
                print(f"   ❌ Cliente necesita índice FAISS")
                needs_repair = True
                
                # Crear índice FAISS
                print(f"      🔄 Creando índice FAISS...")
                faiss_index = vector_manager.create_faiss_index_for_client(client.id)
                if faiss_index:
                    print(f"      ✅ Índice FAISS creado con {faiss_index.total_vectors} vectores")
                else:
                    print(f"      ❌ Error creando índice FAISS")
            
            if needs_repair:
                clients_fixed += 1
                print(f"   ✅ Cliente reparado exitosamente")
            else:
                print(f"   ✅ Cliente ya está funcionando correctamente")
        
        print(f"\n🎉 REPARACIÓN COMPLETADA")
        print(f"   Clientes procesados: {len(all_clients)}")
        print(f"   Clientes reparados: {clients_fixed}")
        print(f"   Clientes que ya estaban bien: {len(all_clients) - clients_fixed}")
        
        return clients_fixed > 0

def test_client_functionality(client_public_id):
    """
    Prueba la funcionalidad de un cliente específico.
    """
    app = create_app()
    with app.app_context():
        print(f"\n🧪 PROBANDO CLIENTE: {client_public_id}")
        print("=" * 50)
        
        # Buscar cliente
        client = Client.query.filter_by(public_id=client_public_id).first()
        if not client:
            print("❌ Cliente no encontrado")
            return False
        
        # Verificar componentes
        documents = Document.query.filter_by(client_id=client.id).all()
        embeddings = Embedding.query.filter_by(client_id=client.id).all()
        faiss_indexes = FAISSIndex.query.filter_by(client_id=client.id, is_active=True).all()
        
        print(f"✅ Cliente: {client.name}")
        print(f"✅ Documentos: {len(documents)}")
        print(f"✅ Embeddings: {len(embeddings)}")
        print(f"✅ Índices FAISS: {len(faiss_indexes)}")
        
        if documents and embeddings and faiss_indexes:
            print("🎉 Cliente completamente funcional!")
            
            # Probar búsqueda
            from modules.vector_manager import VectorManager
            vm = VectorManager()
            results = vm.search_similar_chunks(client.id, "casa precio", top_k=2)
            print(f"✅ Búsqueda de prueba: {len(results)} resultados")
            
            return True
        else:
            print("❌ Cliente no está completamente configurado")
            return False

if __name__ == "__main__":
    print("🚀 HERRAMIENTA DE AUTO-REPARACIÓN")
    
    # Reparar todos los clientes
    fixed = auto_fix_all_clients()
    
    # Probar cliente demo específicamente
    test_client_functionality("demo-client-12345")
    
    if fixed:
        print("\n✨ ¡Sistema reparado! Ahora todos los clientes deberían funcionar correctamente.")
        print("🌐 Prueba en: http://127.0.0.1:5000/pagina_cliente_ejemplo.html")
    else:
        print("\n✅ Sistema ya estaba funcionando correctamente.")