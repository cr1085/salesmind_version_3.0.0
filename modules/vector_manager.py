# modules/vector_manager.py
import numpy as np
import faiss
import pickle
import io
import json
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Union
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.schema.document import Document as LangchainDoc
from langchain_community.embeddings import OllamaEmbeddings

from .models import Embedding, FAISSIndex, Document, Client
from . import db
from config import Config

class VectorManager:
    """
    Gestor de vectores y embeddings que almacena todo en PostgreSQL.
    """
    
    def __init__(self):
        self.embedding_model = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1200, 
            chunk_overlap=200
        )
    
    # def _get_embedding_model(self):
    #     """Inicializa el modelo de embeddings si no está cargado."""
    #     if self.embedding_model is None:
    #         self.embedding_model = GoogleGenerativeAIEmbeddings(
    #             model="models/text-embedding-004",
    #             google_api_key=Config.GOOGLE_API_KEY
    #         )
    #     return self.embedding_model
    def _get_embedding_model(self):
        """Inicializa el modelo de embeddings para Ollama."""
        if self.embedding_model is None:
            # --- ESTE ES EL CAMBIO ---
            # Usamos un modelo específico de Ollama para embeddings
            print("🧠 Usando modelo de embeddings de Ollama (nomic-embed-text)")
            self.embedding_model = OllamaEmbeddings(
                model="nomic-embed-text"
            )
        return self.embedding_model
    
    def _serialize_vector(self, vector: np.ndarray) -> bytes:
        """
        Serializa un vector numpy a bytes para PostgreSQL.
        Usa pickle nativo de Python (compatible con 3.8+).
        """
        import pickle
        return pickle.dumps(vector.astype(np.float32), protocol=pickle.HIGHEST_PROTOCOL)
    
    def _deserialize_vector(self, vector_bytes: bytes) -> np.ndarray:
        """
        Deserializa bytes a vector numpy.
        Usa pickle nativo de Python.
        """
        import pickle
        return pickle.loads(vector_bytes)
    
    def create_embeddings_from_document(self, document_id: int) -> List[Embedding]:
        """
        Crea embeddings para un documento y los guarda en PostgreSQL.
        
        Args:
            document_id: ID del documento en PostgreSQL
            
        Returns:
            Lista de embeddings creados
        """
        try:
            # Obtener documento de PostgreSQL
            document = Document.query.get(document_id)
            if not document or not document.extracted_text:
                print(f"❌ Documento no encontrado o sin texto: {document_id}")
                return []
            
            print(f"📄 Procesando documento: {document.filename}")
            print(f"   - Cliente: {document.client_id}")
            print(f"   - Texto: {len(document.extracted_text):,} caracteres")
            
            # Dividir texto en chunks
            chunks = self.text_splitter.split_text(document.extracted_text)
            print(f"   - Chunks generados: {len(chunks)}")
            
            if not chunks:
                print("⚠️ No se generaron chunks del texto")
                return []
            
            # Obtener modelo de embeddings
            embedding_model = self._get_embedding_model()
            
            # Crear embeddings para cada chunk
            embeddings_created = []
            
            for i, chunk_text in enumerate(chunks):
                try:
                    # Generar embedding para el chunk
                    chunk_vector = embedding_model.embed_query(chunk_text)
                    vector_array = np.array(chunk_vector, dtype=np.float32)
                    
                    # Serializar vector para PostgreSQL
                    serialized_vector = self._serialize_vector(vector_array)
                    
                    # Crear embedding en PostgreSQL
                    embedding = Embedding(
                        client_id=document.client_id,
                        document_id=document_id,
                        text_chunk=chunk_text,
                        chunk_index=i,
                        embedding_vector=serialized_vector,
                        vector_dimension=len(chunk_vector),
                        model_used="text-embedding-004"
                    )
                    
                    db.session.add(embedding)
                    embeddings_created.append(embedding)
                    
                    if (i + 1) % 10 == 0:  # Log cada 10 chunks
                        print(f"   - Procesados {i + 1}/{len(chunks)} chunks")
                
                except Exception as e:
                    print(f"❌ Error procesando chunk {i}: {e}")
                    continue
            
            # Commit todos los embeddings
            db.session.commit()
            
            # Marcar documento como procesado
            document.processed_date = datetime.utcnow()
            db.session.commit()
            
            print(f"✅ {len(embeddings_created)} embeddings creados para {document.filename}")
            return embeddings_created
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creando embeddings para documento {document_id}: {e}")
            return []
    
    def create_faiss_index_for_client(self, client_id: int, index_name: str = "main_index") -> Optional[FAISSIndex]:
        """
        Crea un índice FAISS desde todos los embeddings de un cliente y lo guarda en PostgreSQL.
        
        Args:
            client_id: ID del cliente
            index_name: Nombre del índice
            
        Returns:
            FAISSIndex creado o None si hay error
        """
        try:
            # Obtener todos los embeddings del cliente
            embeddings = Embedding.query.filter_by(client_id=client_id).all()
            
            if not embeddings:
                print(f"❌ No hay embeddings para el cliente {client_id}")
                return None
            
            print(f"🔧 Creando índice FAISS para cliente {client_id}")
            print(f"   - Embeddings disponibles: {len(embeddings)}")
            
            # Verificar dimensiones
            first_embedding = embeddings[0]
            vector_dimension = first_embedding.vector_dimension
            print(f"   - Dimensión de vectores: {vector_dimension}")
            
            # Crear índice FAISS
            index = faiss.IndexFlatL2(vector_dimension)
            
            # Cargar vectores y añadir al índice
            vectors = []
            for embedding in embeddings:
                vector = self._deserialize_vector(embedding.embedding_vector)
                vectors.append(vector)
            
            # Convertir a matriz numpy y añadir al índice
            vectors_matrix = np.vstack(vectors).astype(np.float32)
            index.add(vectors_matrix)
            
            print(f"   - Vectores añadidos al índice: {index.ntotal}")
            
            # Serializar índice FAISS para PostgreSQL
            index_buffer = io.BytesIO()
            faiss.write_index(index, faiss.PyCallbackIOWriter(index_buffer.write))
            index_data = index_buffer.getvalue()
            
            # Crear metadatos
            metadata = {
                "embedding_ids": [emb.id for emb in embeddings],
                "creation_date": datetime.utcnow().isoformat(),
                "model_used": "text-embedding-004",
                "chunk_size": 1200,
                "chunk_overlap": 200
            }
            
            # Desactivar índice anterior si existe
            old_index = FAISSIndex.query.filter_by(
                client_id=client_id, 
                index_name=index_name,
                is_active=True
            ).first()
            
            if old_index:
                old_index.is_active = False
                old_index.version += 1
            
            # Crear nuevo índice en PostgreSQL
            new_index = FAISSIndex(
                client_id=client_id,
                index_name=index_name,
                index_data=index_data,
                index_metadata=json.dumps(metadata),
                vector_dimension=vector_dimension,
                total_vectors=len(vectors),
                index_type="IndexFlatL2",
                is_active=True,
                version=1
            )
            
            db.session.add(new_index)
            db.session.commit()
            
            print(f"✅ Índice FAISS creado y guardado en PostgreSQL")
            print(f"   - ID del índice: {new_index.id}")
            print(f"   - Tamaño: {len(index_data):,} bytes")
            
            return new_index
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creando índice FAISS para cliente {client_id}: {e}")
            return None
    
    def load_faiss_index_for_client(self, client_id: int, index_name: str = "main_index") -> Optional[Tuple[faiss.Index, List[Embedding]]]:
        """
        Carga un índice FAISS desde PostgreSQL.
        
        Args:
            client_id: ID del cliente
            index_name: Nombre del índice
            
        Returns:
            Tupla (índice FAISS, lista de embeddings) o None si no existe
        """
        try:
            # Buscar índice activo en PostgreSQL
            faiss_index_record = FAISSIndex.query.filter_by(
                client_id=client_id,
                index_name=index_name,
                is_active=True
            ).first()
            
            if not faiss_index_record:
                print(f"❌ Índice FAISS no encontrado: cliente={client_id}, nombre={index_name}")
                return None
            
            print(f"📖 Cargando índice FAISS desde PostgreSQL")
            print(f"   - Cliente: {client_id}")
            print(f"   - Índice: {index_name}")
            print(f"   - Vectores: {faiss_index_record.total_vectors}")
            
            # Deserializar índice FAISS
            index_buffer = io.BytesIO(faiss_index_record.index_data)
            index = faiss.read_index(faiss.PyCallbackIOReader(index_buffer.read))
            
            # Obtener embeddings asociados (en el mismo orden)
            metadata = json.loads(faiss_index_record.index_metadata)
            embedding_ids = metadata.get("embedding_ids", [])
            
            # Cargar embeddings en el orden correcto
            embeddings = []
            for emb_id in embedding_ids:
                embedding = Embedding.query.get(emb_id)
                if embedding:
                    embeddings.append(embedding)
            
            print(f"✅ Índice FAISS cargado exitosamente")
            print(f"   - Embeddings asociados: {len(embeddings)}")
            
            return index, embeddings
            
        except Exception as e:
            print(f"❌ Error cargando índice FAISS: {e}")
            return None
    
    def search_similar_chunks(self, client_id: int, query: str, top_k: int = 3) -> List[Dict]:
        """
        Busca chunks similares usando FAISS desde PostgreSQL.
        
        Args:
            client_id: ID del cliente
            query: Consulta de búsqueda
            top_k: Número de resultados más similares
            
        Returns:
            Lista de diccionarios con chunks similares y sus scores
        """
        try:
            # Cargar índice FAISS del cliente
            faiss_data = self.load_faiss_index_for_client(client_id)
            if not faiss_data:
                print(f"❌ No se pudo cargar índice para cliente {client_id}")
                return []
            
            index, embeddings = faiss_data
            
            # Generar embedding para la consulta
            embedding_model = self._get_embedding_model()
            query_vector = embedding_model.embed_query(query)
            query_array = np.array([query_vector], dtype=np.float32)
            
            # Buscar en el índice FAISS
            scores, indices = index.search(query_array, min(top_k, len(embeddings)))
            
            # Construir resultados
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(embeddings):  # Verificar índice válido
                    embedding = embeddings[idx]
                    results.append({
                        'text': embedding.text_chunk,
                        'score': float(score),
                        'document_id': embedding.document_id,
                        'chunk_index': embedding.chunk_index,
                        'embedding_id': embedding.id
                    })
            
            print(f"🔍 Búsqueda completada: {len(results)} resultados para '{query[:50]}...'")
            return results
            
        except Exception as e:
            print(f"❌ Error en búsqueda: {e}")
            return []
    
    def get_client_vector_stats(self, client_id: int) -> Dict:
        """
        Obtiene estadísticas de vectores para un cliente.
        
        Args:
            client_id: ID del cliente
            
        Returns:
            Diccionario con estadísticas
        """
        try:
            embeddings_count = Embedding.query.filter_by(client_id=client_id).count()
            indexes_count = FAISSIndex.query.filter_by(client_id=client_id).count()
            active_indexes = FAISSIndex.query.filter_by(client_id=client_id, is_active=True).count()
            
            # Tamaño total de embeddings
            embeddings = Embedding.query.filter_by(client_id=client_id).all()
            total_embedding_size = sum(len(emb.embedding_vector) for emb in embeddings)
            
            # Tamaño de índices FAISS
            indexes = FAISSIndex.query.filter_by(client_id=client_id).all()
            total_index_size = sum(len(idx.index_data) for idx in indexes)
            
            return {
                'total_embeddings': embeddings_count,
                'total_indexes': indexes_count,
                'active_indexes': active_indexes,
                'embeddings_size_bytes': total_embedding_size,
                'indexes_size_bytes': total_index_size,
                'total_size_bytes': total_embedding_size + total_index_size,
                'total_size_mb': round((total_embedding_size + total_index_size) / (1024 * 1024), 2)
            }
            
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas: {e}")
            return {}
    
    def rebuild_client_index(self, client_id: int) -> bool:
        """
        Reconstruye completamente el índice FAISS de un cliente.
        
        Args:
            client_id: ID del cliente
            
        Returns:
            True si se reconstruyó exitosamente
        """
        try:
            print(f"🔄 Reconstruyendo índice para cliente {client_id}")
            
            # Crear nuevo índice
            new_index = self.create_faiss_index_for_client(client_id, "main_index")
            
            if new_index:
                print(f"✅ Índice reconstruido exitosamente")
                return True
            else:
                print(f"❌ Falló la reconstrucción del índice")
                return False
                
        except Exception as e:
            print(f"❌ Error reconstruyendo índice: {e}")
            return False