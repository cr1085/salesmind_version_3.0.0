# indexer.py - MIGRADO A POSTGRESQL
import os
from typing import Optional
from config import Config
from modules.document_manager import DocumentManager
from modules.vector_manager import VectorManager
from modules.models import Client
from modules import db

def create_client_index(pdfs_path: str, client_id: int, index_save_path: str = None) -> bool:
    """
    Crea un índice completo para un cliente usando PostgreSQL.
    NUEVA VERSIÓN: Todo se almacena en PostgreSQL, no en archivos.
    
    Args:
        pdfs_path: Ruta a la carpeta con PDFs
        client_id: ID del cliente en PostgreSQL
        index_save_path: DEPRECATED - ya no se usa, mantenido por compatibilidad
    
    Returns:
        True si tiene éxito, False si falla
    """
    print(f"🚀 === CREANDO ÍNDICE POSTGRESQL PARA CLIENTE {client_id} ===")
    print(f"📂 Carpeta de PDFs: {pdfs_path}")
    
    if not Config.GOOGLE_API_KEY:
        print("❌ ERROR: GOOGLE_API_KEY no encontrada en .env.")
        return False

    if not os.path.exists(pdfs_path):
        print(f"❌ ERROR: La ruta de PDFs '{pdfs_path}' no existe.")
        return False
    
    # Verificar que el cliente existe
    client = Client.query.get(client_id)
    if not client:
        print(f"❌ ERROR: Cliente con ID {client_id} no encontrado.")
        return False
    
    print(f"👤 Cliente: {client.name}")
    
    try:
        # PASO 1: Gestionar documentos
        print("\n📄 PASO 1: Procesando documentos...")
        doc_manager = DocumentManager()
        documents = doc_manager.add_documents_from_folder(client_id, pdfs_path)
        
        if not documents:
            print("❌ ERROR: No se procesaron documentos correctamente.")
            return False
        
        print(f"✅ {len(documents)} documentos guardados en PostgreSQL")
        
        # PASO 2: Crear embeddings
        print("\n🧮 PASO 2: Generando embeddings...")
        vector_manager = VectorManager()
        total_embeddings = 0
        
        for document in documents:
            embeddings = vector_manager.create_embeddings_from_document(document.id)
            total_embeddings += len(embeddings)
        
        if total_embeddings == 0:
            print("❌ ERROR: No se generaron embeddings.")
            return False
        
        print(f"✅ {total_embeddings} embeddings creados en PostgreSQL")
        
        # PASO 3: Crear índice FAISS
        print("\n🔧 PASO 3: Creando índice FAISS...")
        faiss_index = vector_manager.create_faiss_index_for_client(client_id, "main_index")
        
        if not faiss_index:
            print("❌ ERROR: No se pudo crear el índice FAISS.")
            return False
        
        print(f"✅ Índice FAISS creado en PostgreSQL (ID: {faiss_index.id})")
        
        # PASO 4: Actualizar cliente (marcar como listo)
        print("\n👤 PASO 4: Actualizando cliente...")
        client.index_path = f"postgresql://client_{client_id}"  # Marcador simbólico
        db.session.commit()
        
        # PASO 5: Mostrar estadísticas finales
        print("\n📊 RESUMEN FINAL:")
        doc_stats = doc_manager.get_documents_stats(client_id)
        vector_stats = vector_manager.get_client_vector_stats(client_id)
        
        print(f"   📄 Documentos: {doc_stats['total_documents']}")
        print(f"   📝 Texto extraído: {doc_stats['total_text_chars']:,} caracteres")
        print(f"   📦 Tamaño total: {doc_stats['total_size_mb']} MB")
        print(f"   🧮 Embeddings: {vector_stats['total_embeddings']}")
        print(f"   🔧 Índices FAISS: {vector_stats['active_indexes']}")
        print(f"   💾 Tamaño vectores: {vector_stats['total_size_mb']} MB")
        
        print(f"\n🎉 ¡ÍNDICE POSTGRESQL CREADO EXITOSAMENTE!")
        print(f"   Cliente: {client.name}")
        print(f"   ID: {client_id}")
        print(f"   Public ID: {client.public_id}")
        
        return True
        
    except Exception as e:
        print(f"\n💥 ERROR CRÍTICO durante la indexación:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def create_client_index_legacy(pdfs_path: str, index_save_path: str) -> bool:
    """
    FUNCIÓN LEGACY: Mantiene compatibilidad con el código existente.
    Redirige a la nueva función basada en PostgreSQL.
    
    DEPRECATED: Use create_client_index(pdfs_path, client_id) instead
    """
    print("⚠️ ADVERTENCIA: Usando función legacy de indexación")
    print("⚠️ Se requiere especificar client_id para usar PostgreSQL")
    print("⚠️ Esta función está deprecada y podría no funcionar correctamente")
    
    # Intentar extraer client_id del path (hack temporal)
    import re
    client_match = re.search(r'client_(\d+)', index_save_path)
    if client_match:
        client_id = int(client_match.group(1))
        print(f"🔄 Redirigiendo a PostgreSQL con client_id: {client_id}")
        return create_client_index(pdfs_path, client_id, index_save_path)
    else:
        print("❌ No se pudo extraer client_id del path. Función legacy no soportada.")
        return False


# Funciones auxiliares para compatibilidad
def get_client_index_info(client_id: int) -> dict:
    """
    Obtiene información completa del índice de un cliente desde PostgreSQL.
    
    Args:
        client_id: ID del cliente
        
    Returns:
        Diccionario con información del índice
    """
    from modules.document_manager import DocumentManager
    from modules.vector_manager import VectorManager
    
    try:
        client = Client.query.get(client_id)
        if not client:
            return {"error": "Cliente no encontrado"}
        
        doc_manager = DocumentManager()
        vector_manager = VectorManager()
        
        doc_stats = doc_manager.get_documents_stats(client_id)
        vector_stats = vector_manager.get_client_vector_stats(client_id)
        
        return {
            "client_name": client.name,
            "client_id": client_id,
            "public_id": client.public_id,
            "created_at": client.created_at.isoformat(),
            "documents": doc_stats,
            "vectors": vector_stats,
            "status": "ready" if vector_stats.get("active_indexes", 0) > 0 else "pending"
        }
        
    except Exception as e:
        return {"error": str(e)}
    # Esta función está deprecated - mantenida solo por compatibilidad
    try:
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004", google_api_key=Config.GOOGLE_API_KEY
        )
        vector_store = FAISS.from_documents(all_chunks, embedding=embeddings)
        
        # Guardamos el índice en la ruta específica del cliente
        vector_store.save_local(index_save_path)
        
        print(f"-> ¡ÉXITO! Índice para cliente creado en '{index_save_path}'.")
        return True
    except Exception as e:
        print(f"\n-> ERROR CRÍTICO durante la creación de embeddings: {e}")
        traceback.print_exc()
        return False

def get_client_index_info(client_id: int) -> dict:
    """
    Obtiene información completa del índice de un cliente para la interfaz admin.
    """
    try:
        from modules.models import Document, Embedding, FAISSIndex, Conversation
        
        client = Client.query.get(client_id)
        if not client:
            return {"error": f"Cliente {client_id} no encontrado"}
        
        # Contar documentos
        total_documents = Document.query.filter_by(client_id=client_id).count()
        
        # Contar embeddings y calcular tamaño
        embeddings = Embedding.query.filter_by(client_id=client_id).all()
        total_embeddings = len(embeddings)
        total_size_bytes = sum(len(emb.embedding_vector) for emb in embeddings)
        total_size_mb = total_size_bytes / (1024 * 1024)
        
        # Información de índices FAISS
        faiss_indexes = FAISSIndex.query.filter_by(client_id=client_id).all()
        faiss_info = {
            "count": len(faiss_indexes),
            "active": len([idx for idx in faiss_indexes if idx.is_active]),
            "total_vectors": sum(idx.total_vectors for idx in faiss_indexes),
            "indexes": [
                {
                    "name": idx.index_name,
                    "vectors": idx.total_vectors,
                    "dimension": idx.vector_dimension,
                    "type": idx.index_type,
                    "active": idx.is_active,
                    "created": idx.created_at.strftime('%Y-%m-%d %H:%M:%S') if idx.created_at else None,
                    "updated": idx.updated_at.strftime('%Y-%m-%d %H:%M:%S') if idx.updated_at else None
                }
                for idx in faiss_indexes
            ]
        }
        
        # Estadísticas de conversaciones
        total_conversations = Conversation.query.filter_by(client_id=client_id).count()
        
        return {
            "client": {
                "id": client.id,
                "name": client.name,
                "public_id": str(client.public_id),
                "created_at": client.created_at.strftime('%Y-%m-%d %H:%M:%S') if client.created_at else None
            },
            "documents": {
                "total_documents": total_documents,
                "processed": total_documents  # Asumimos que todos están procesados
            },
            "vectors": {
                "total_embeddings": total_embeddings,
                "total_size_bytes": total_size_bytes,
                "total_size_mb": round(total_size_mb, 2)
            },
            "faiss": faiss_info,
            "conversations": {
                "total": total_conversations
            },
            "status": "active" if total_documents > 0 else "empty"
        }
        
    except Exception as e:
        return {"error": str(e)}

def get_client_documents(client_id: int) -> list:
    """
    Obtiene la lista de documentos de un cliente con información detallada.
    """
    try:
        from modules.models import Document
        
        documents = Document.query.filter_by(client_id=client_id).order_by(Document.upload_date.desc()).all()
        
        docs_info = []
        for doc in documents:
            docs_info.append({
                "id": doc.id,
                "filename": doc.filename,
                "file_type": doc.file_type,
                "file_size": doc.file_size,
                "file_size_mb": round(doc.file_size / (1024 * 1024), 2),
                "upload_date": doc.upload_date.strftime('%Y-%m-%d %H:%M:%S') if doc.upload_date else None,
                "processed_date": doc.processed_date.strftime('%Y-%m-%d %H:%M:%S') if doc.processed_date else None,
                "is_processed": doc.is_processed,
                "content_hash": doc.content_hash,
                "text_preview": doc.extracted_text[:200] + "..." if doc.extracted_text and len(doc.extracted_text) > 200 else doc.extracted_text
            })
        
        return docs_info
        
    except Exception as e:
        return [{"error": str(e)}]