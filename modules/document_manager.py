# modules/document_manager.py
import hashlib
import os
import fitz  # PyMuPDF
import io
from datetime import datetime
from typing import Optional, List, Dict, Tuple
from .models import Document, Client, Embedding, FAISSIndex
from . import db
from sqlalchemy.exc import IntegrityError

class DocumentManager:
    """
    Gestor de documentos que almacena PDFs y su contenido en PostgreSQL.
    """
    
    @staticmethod
    def calculate_file_hash(file_content: bytes) -> str:
        """Calcula el hash SHA-256 del contenido del archivo."""
        return hashlib.sha256(file_content).hexdigest()
    
    @staticmethod
    def extract_text_from_pdf(file_content: bytes) -> str:
        """
        Extrae texto de un PDF almacenado como bytes.
        """
        try:
            # Crear un objeto BytesIO desde los bytes
            pdf_stream = io.BytesIO(file_content)
            
            # Abrir PDF con PyMuPDF
            with fitz.open(stream=pdf_stream, filetype="pdf") as doc:
                full_text = ""
                for page in doc:
                    full_text += page.get_text()
                    full_text += "\n\n"  # Separar páginas
                
                return full_text.strip()
        
        except Exception as e:
            print(f"❌ Error extrayendo texto del PDF: {e}")
            return ""
    
    @classmethod
    def add_document_from_file(cls, client_id: int, file_path: str) -> Optional[Document]:
        """
        Añade un documento desde una ruta de archivo al PostgreSQL.
        
        Args:
            client_id: ID del cliente
            file_path: Ruta completa al archivo
            
        Returns:
            Document object si se crea exitosamente, None si hay error
        """
        try:
            # Validar que el archivo existe
            if not os.path.exists(file_path):
                print(f"❌ Archivo no encontrado: {file_path}")
                return None
            
            # Obtener información del archivo
            filename = os.path.basename(file_path)
            file_extension = filename.lower().split('.')[-1] if '.' in filename else 'unknown'
            file_size = os.path.getsize(file_path)
            
            # Leer contenido del archivo
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            # Calcular hash para evitar duplicados por cliente
            content_hash = cls.calculate_file_hash(file_content)
            
            # Verificar si ya existe este documento para este cliente específico
            existing_doc = Document.query.filter_by(
                client_id=client_id, 
                content_hash=content_hash
            ).first()
            if existing_doc:
                print(f"⚠️ Documento ya existe para este cliente: {filename} (hash: {content_hash[:8]}...)")
                return existing_doc
            
            # Extraer texto según el tipo de archivo
            extracted_text = ""
            if file_extension == 'pdf':
                extracted_text = cls.extract_text_from_pdf(file_content)
            else:
                print(f"⚠️ Tipo de archivo no soportado para extracción de texto: {file_extension}")
            
            # Crear nuevo documento en PostgreSQL
            new_document = Document(
                client_id=client_id,
                filename=filename,
                file_type=file_extension,
                file_size=file_size,
                file_content=file_content,
                extracted_text=extracted_text,
                content_hash=content_hash,
                is_processed=bool(extracted_text)  # True si se extrajo texto exitosamente
            )
            
            db.session.add(new_document)
            db.session.commit()
            
            print(f"✅ Documento guardado en PostgreSQL: {filename}")
            print(f"   - Tamaño: {file_size:,} bytes")
            print(f"   - Texto extraído: {len(extracted_text):,} caracteres")
            print(f"   - Hash: {content_hash[:16]}...")
            
            return new_document
            
        except IntegrityError as e:
            db.session.rollback()
            print(f"❌ Error de integridad al guardar documento: {e}")
            return None
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error al procesar documento {file_path}: {e}")
            return None
    
    @classmethod
    def add_documents_from_folder(cls, client_id: int, folder_path: str) -> List[Document]:
        """
        Añade todos los PDFs de una carpeta a PostgreSQL.
        
        Args:
            client_id: ID del cliente
            folder_path: Ruta a la carpeta con PDFs
            
        Returns:
            Lista de documentos creados exitosamente
        """
        documents_added = []
        
        if not os.path.exists(folder_path):
            print(f"❌ Carpeta no encontrada: {folder_path}")
            return documents_added
        
        # Buscar archivos PDF en la carpeta
        pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]
        
        if not pdf_files:
            print(f"⚠️ No se encontraron archivos PDF en: {folder_path}")
            return documents_added
        
        print(f"📁 Procesando {len(pdf_files)} archivos PDF...")
        
        for pdf_file in pdf_files:
            file_path = os.path.join(folder_path, pdf_file)
            document = cls.add_document_from_file(client_id, file_path)
            
            if document:
                documents_added.append(document)
        
        print(f"✅ {len(documents_added)} documentos añadidos exitosamente a PostgreSQL")
        return documents_added
    
    @classmethod
    def get_client_documents(cls, client_id: int, processed_only: bool = True) -> List[Document]:
        """
        Obtiene todos los documentos de un cliente.
        
        Args:
            client_id: ID del cliente
            processed_only: Si True, solo devuelve documentos con texto extraído
            
        Returns:
            Lista de documentos
        """
        query = Document.query.filter_by(client_id=client_id)
        
        if processed_only:
            query = query.filter_by(is_processed=True)
        
        return query.order_by(Document.upload_date.desc()).all()
    
    @classmethod
    def get_document_content(cls, document_id: int) -> Optional[bytes]:
        """
        Obtiene el contenido binario de un documento.
        
        Args:
            document_id: ID del documento
            
        Returns:
            Contenido del archivo como bytes o None si no existe
        """
        document = Document.query.get(document_id)
        return document.file_content if document else None
    
    @classmethod
    def delete_document(cls, document_id: int, client_id: int) -> bool:
        """
        Elimina un documento de PostgreSQL.
        
        Args:
            document_id: ID del documento
            client_id: ID del cliente (para verificar propiedad)
            
        Returns:
            True si se eliminó exitosamente, False en caso contrario
        """
        try:
            document = Document.query.filter_by(id=document_id, client_id=client_id).first()
            
            if not document:
                print(f"❌ Documento no encontrado o no pertenece al cliente")
                return False
            
            # Eliminar también embeddings asociados (cascade)
            db.session.delete(document)
            db.session.commit()
            
            print(f"✅ Documento eliminado: {document.filename}")
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error al eliminar documento: {e}")
            return False
    
    @classmethod
    def get_documents_stats(cls, client_id: int) -> Dict:
        """
        Obtiene estadísticas de documentos de un cliente.
        
        Args:
            client_id: ID del cliente
            
        Returns:
            Diccionario con estadísticas
        """
        documents = cls.get_client_documents(client_id, processed_only=False)
        
        total_size = sum(doc.file_size for doc in documents)
        total_text = sum(len(doc.extracted_text or '') for doc in documents)
        processed_count = sum(1 for doc in documents if doc.is_processed)
        
        return {
            'total_documents': len(documents),
            'processed_documents': processed_count,
            'pending_documents': len(documents) - processed_count,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'total_text_chars': total_text,
            'avg_text_per_doc': round(total_text / len(documents), 0) if documents else 0
        }