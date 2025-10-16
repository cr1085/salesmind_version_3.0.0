# modules/models.py
from . import db
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import BYTEA, TEXT

class Client(db.Model):
    """
    Representa a un cliente que usará una instancia del agente SalesMind.
    """
    # --- Campos Principales ---
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    
    # Clave pública que se usará en el widget de JavaScript.
    # Se genera un valor único por defecto (ej: 'c7a4g2f9-1e2a-4c3d-b5a6-8f9d0a1b2c3d')
    public_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # --- Configuración Específica del Agente ---
    # DEPRECATED: Ya no usamos rutas de archivos, todo está en PostgreSQL
    index_path = db.Column(db.String(255), nullable=True, default="postgresql_storage")
    
    # ID del chat de Telegram al que se enviarán las notificaciones para este cliente.
    telegram_chat_id = db.Column(db.String(100), nullable=True)
    
    # --- Metadatos ---
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # --- Relaciones ---
    conversations = db.relationship('Conversation', backref='client', lazy=True, cascade='all, delete-orphan')
    documents = db.relationship('Document', backref='client', lazy=True, cascade='all, delete-orphan')
    embeddings = db.relationship('Embedding', backref='client', lazy=True, cascade='all, delete-orphan')
    faiss_indexes = db.relationship('FAISSIndex', backref='client', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Client {self.name}>'


class Conversation(db.Model):
    """
    Almacena todas las conversaciones de los clientes (antes en SQLite).
    Usa tabla específica para evitar conflictos.
    """
    __tablename__ = 'salesmind_conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    chat_id = db.Column(db.String(100), nullable=False)  # ID del chat de Telegram o web
    sender = db.Column(db.String(50), nullable=False)    # 'user', 'bot', 'assistant'
    message_text = db.Column(TEXT, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Metadatos adicionales
    message_type = db.Column(db.String(20), default='text')  # 'text', 'image', 'document'
    platform = db.Column(db.String(20), default='web')      # 'web', 'telegram'
    
    def __repr__(self):
        return f'<Conversation {self.chat_id}: {self.sender}>'


class Document(db.Model):
    """
    Almacena el contenido completo de los PDFs y documentos (antes en sistema de archivos).
    Usa una tabla específica para evitar conflictos con tablas existentes.
    """
    __tablename__ = 'salesmind_documents'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)    # 'pdf', 'docx', 'txt'
    file_size = db.Column(db.Integer, nullable=False)       # Tamaño en bytes
    
    # Contenido del archivo
    file_content = db.Column(BYTEA, nullable=False)         # Archivo binario completo
    extracted_text = db.Column(TEXT, nullable=True)         # Texto extraído del documento
    
    # Metadatos
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    processed_date = db.Column(db.DateTime, nullable=True)
    is_processed = db.Column(db.Boolean, default=False)
    
    # Hash del contenido para evitar duplicados por cliente
    content_hash = db.Column(db.String(64), nullable=False)
    
    # Restricción única: un cliente no puede tener el mismo documento duplicado
    __table_args__ = (
        db.UniqueConstraint('client_id', 'content_hash', name='unique_client_document'),
    )
    
    def __repr__(self):
        return f'<Document {self.filename} - Client: {self.client_id}>'


class Embedding(db.Model):
    """
    Almacena los embeddings/vectores individuales de cada chunk de texto.
    Reutiliza la tabla embeddings existente que ya tiene la estructura correcta.
    """
    __tablename__ = 'embeddings'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    document_id = db.Column(db.Integer, db.ForeignKey('salesmind_documents.id'), nullable=False)
    
    # Contenido del chunk
    text_chunk = db.Column(TEXT, nullable=False)
    chunk_index = db.Column(db.Integer, nullable=False)     # Posición dentro del documento
    
    # Vector de embedding (serializado como bytes)
    embedding_vector = db.Column(BYTEA, nullable=False)     # Vector numpy serializado
    vector_dimension = db.Column(db.Integer, nullable=False) # Ej: 384, 1536, etc.
    
    # Metadatos
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    model_used = db.Column(db.String(100), nullable=False)  # 'text-embedding-004', 'all-MiniLM-L6-v2'
    
    # Relación con documento (especificar foreign_keys explícitamente)
    document = db.relationship('Document', backref='embeddings', foreign_keys=[document_id])
    
    def __repr__(self):
        return f'<Embedding {self.id} - Doc: {self.document_id}>'


class FAISSIndex(db.Model):
    """
    Almacena los índices FAISS completos como datos binarios (antes en archivos .faiss).
    """
    __tablename__ = 'faiss_indexes'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    
    # Datos del índice FAISS
    index_name = db.Column(db.String(100), nullable=False)   # 'main_index', 'backup_20251013'
    index_data = db.Column(BYTEA, nullable=False)           # Índice FAISS serializado
    index_metadata = db.Column(TEXT, nullable=True)         # JSON con metadatos
    
    # Información técnica
    vector_dimension = db.Column(db.Integer, nullable=False)
    total_vectors = db.Column(db.Integer, nullable=False)
    index_type = db.Column(db.String(50), default='IndexFlatL2')
    
    # Control de versiones
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    version = db.Column(db.Integer, default=1)
    
    def __repr__(self):
        return f'<FAISSIndex {self.index_name} - Client: {self.client_id}>'


class QueryLog(db.Model):
    """
    Registro de todas las consultas realizadas al sistema (antes parcialmente en SQLite).
    """
    __tablename__ = 'query_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    conversation_id = db.Column(db.Integer, db.ForeignKey('salesmind_conversations.id'), nullable=True)
    
    # Contenido de la consulta
    question = db.Column(TEXT, nullable=False)
    answer = db.Column(TEXT, nullable=True)
    
    # Metadatos técnicos
    response_time = db.Column(db.Float, nullable=True)      # Tiempo de respuesta en segundos
    tokens_used = db.Column(db.Integer, nullable=True)     # Tokens consumidos de la API
    model_used = db.Column(db.String(100), nullable=True)  # Modelo de IA utilizado
    
    # Contexto RAG
    retrieved_chunks = db.Column(db.Integer, nullable=True) # Número de chunks recuperados
    similarity_scores = db.Column(TEXT, nullable=True)      # JSON con scores de similitud
    
    # Timestamp
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    client = db.relationship('Client', backref='query_logs')
    conversation = db.relationship('Conversation', backref='query_logs')
    
    def __repr__(self):
        return f'<QueryLog {self.id} - Client: {self.client_id}>'