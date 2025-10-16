# SalesMind v1.0.0 - Especificaciones Técnicas
## Documentación de Implementación

---

## 📋 **RESUMEN EJECUTIVO**

SalesMind v1.0.0 es un sistema RAG (Retrieval-Augmented Generation) multi-tenant completamente migrado a PostgreSQL, diseñado para proporcionar respuestas inteligentes y contextuales en múltiples idiomas basándose en documentos específicos de cada cliente empresarial.

---

## 🏗️ **ARQUITECTURA DEL SISTEMA**

### **Componentes Principales:**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │     Backend     │    │   PostgreSQL    │
│   (HTML/JS)     │◄──►│    (Flask)      │◄──►│   (Database)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   IA Models     │
                    │ (Ollama/Gemini) │
                    └─────────────────┘
```

### **Flujo de Datos:**
1. **Cliente Web** → Envía consulta por HTTP POST
2. **Flask Router** → Valida cliente y procesa consulta
3. **RAG Engine** → Busca en vectores PostgreSQL
4. **IA Model** → Genera respuesta contextual
5. **Response** → Devuelve respuesta en idioma original

---

## 💾 **ESQUEMA DE BASE DE DATOS**

### **Tabla: `client`**
```sql
CREATE TABLE client (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    public_id UUID NOT NULL UNIQUE,
    index_path VARCHAR(255) DEFAULT 'postgresql_storage',
    telegram_chat_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **Tabla: `salesmind_documents`**
```sql
CREATE TABLE salesmind_documents (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES client(id),
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(10) NOT NULL,
    file_size INTEGER NOT NULL,
    file_content BYTEA NOT NULL,
    extracted_text TEXT,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_date TIMESTAMP,
    is_processed BOOLEAN DEFAULT FALSE,
    content_hash VARCHAR(64) NOT NULL,
    UNIQUE(client_id, content_hash)
);
```

### **Tabla: `embeddings`**
```sql
CREATE TABLE embeddings (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES client(id),
    document_id INTEGER REFERENCES salesmind_documents(id),
    text_chunk TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    embedding_vector BYTEA NOT NULL,
    vector_dimension INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    model_used VARCHAR(100) NOT NULL
);
```

### **Tabla: `faiss_indexes`**
```sql
CREATE TABLE faiss_indexes (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES client(id),
    index_name VARCHAR(100) NOT NULL,
    index_data BYTEA NOT NULL,
    index_metadata TEXT,
    vector_dimension INTEGER NOT NULL,
    total_vectors INTEGER NOT NULL,
    index_type VARCHAR(50) DEFAULT 'IndexFlatL2',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    version INTEGER DEFAULT 1
);
```

---

## 🔧 **COMPONENTES TÉCNICOS DETALLADOS**

### **1. Document Manager (`modules/document_manager.py`)**
```python
class DocumentManager:
    - add_document_from_file(client_id, file_path)
    - add_documents_from_folder(client_id, folder_path) 
    - extract_text_from_pdf(file_content)
    - calculate_file_hash(file_content)
```

**Funcionalidades:**
- Extracción de texto de PDFs
- Deduplicación por hash SHA-256
- Almacenamiento binario en PostgreSQL
- Gestión de metadatos

### **2. Vector Manager (`modules/vector_manager.py`)**
```python
class VectorManager:
    - create_embeddings_for_document(document_id)
    - create_faiss_index_for_client(client_id)
    - search_similar_chunks(client_id, query, top_k)
    - load_faiss_index_for_client(client_id)
```

**Funcionalidades:**
- Generación de embeddings con Google AI
- Creación de índices FAISS
- Búsqueda de similitud vectorial
- Serialización/deserialización de índices

### **3. RAG Core (`modules/assistant/core.py`)**
```python
def get_commercial_response(question: str, client_id: str) -> str:
    1. Validar cliente por public_id
    2. Buscar chunks similares
    3. Construir contexto
    4. Detectar idioma automáticamente
    5. Generar prompt específico
    6. Obtener respuesta de IA
    7. Retornar respuesta
```

**Características:**
- Detección automática de idioma
- Prompts específicos por idioma
- Soporte para múltiples modelos de IA
- Manejo de errores robusto

---

## 🌍 **SISTEMA MULTIIDIOMA**

### **Detección de Idioma:**
```python
def get_language_specific_prompt(question: str, context: str) -> str:
    # Palabras clave por idioma
    spanish_keywords = ['qué', 'cuánto', 'cómo', 'precio', 'modelo']
    english_keywords = ['what', 'how', 'price', 'model', 'available']
    french_keywords = ['quel', 'comment', 'prix', 'modèle']
    # ... más idiomas
```

### **Prompts Específicos:**
- **Español:** "Eres SalesMind, un asistente de ventas. Tu respuesta debe estar COMPLETAMENTE en español."
- **English:** "You are SalesMind, a sales assistant. Your response must be COMPLETELY in English."
- **Français:** "Vous êtes SalesMind, un assistant de vente. Votre réponse doit être COMPLÈTEMENT en français."

---

## 🔄 **API ENDPOINTS**

### **Chat API (`POST /chat-api`)**
```json
{
    "method": "POST",
    "endpoint": "/chat-api",
    "headers": {
        "Content-Type": "application/json"
    },
    "body": {
        "message": "string",
        "clientId": "uuid-string"
    },
    "response": {
        "reply": "string",
        "status": "success|error"
    }
}
```

### **Flujo de Procesamiento:**
1. Validación de parámetros
2. Búsqueda de cliente por `public_id`
3. Llamada a `get_commercial_response()`
4. Registro en `conversations` y `query_logs`
5. Respuesta JSON al frontend

---

## 🏢 **MULTI-TENANCY**

### **Aislamiento de Datos:**
- **Por Cliente:** Cada empresa tiene datos completamente separados
- **Public ID:** UUID único para identificación externa segura
- **Internal ID:** ID numérico para referencias internas eficientes
- **Validación:** Verificación en cada consulta

### **Gestión de Clientes:**
```python
# Comando CLI para agregar cliente
flask add-client "Empresa ABC" "telegram_id" "carpeta_pdfs"

# Estructura generada:
Client(
    id=auto_increment,
    name="Empresa ABC",
    public_id=uuid4(),
    telegram_chat_id="telegram_id"
)
```

---

## 🚀 **OPTIMIZACIONES DE RENDIMIENTO**

### **Base de Datos:**
- Índices en columnas de búsqueda frecuente
- Transacciones optimizadas
- Conexiones persistentes
- Queries preparadas

### **Vectores:**
- Índices FAISS en memoria
- Búsqueda aproximada (ANN)
- Dimensión optimizada (768)
- Caching de resultados

### **IA:**
- Reutilización de modelos
- Temperatura baja (0.2) para consistencia
- Timeouts configurables
- Fallback automático entre proveedores

---

## 📊 **MÉTRICAS Y MONITOREO**

### **Logs Implementados:**
- **Conversaciones:** Todas las interacciones guardadas
- **Query Logs:** Tiempo de respuesta y modelo usado
- **Errores:** Stack traces completos
- **Performance:** Tiempo de búsqueda vectorial

### **Estadísticas Disponibles:**
```python
# Por cliente:
- Total documentos
- Total embeddings  
- Total conversaciones
- Tamaño de datos
- Tiempo promedio de respuesta
```

---

## 🔒 **CONSIDERACIONES DE SEGURIDAD**

### **Autenticación:**
- Validación de `public_id` en cada request
- No exposición de IDs internos
- Timeouts en consultas largas

### **Autorización:**
- Aislamiento estricto por cliente
- Validación de ownership de documentos
- Sanitización de inputs

### **Datos Sensibles:**
- Almacenamiento seguro en PostgreSQL
- No logs de contenido sensitivo
- Encriptación a nivel de BD (configuración externa)

---

## ⚡ **INSTALACIÓN Y DEPLOYMENT**

### **Requisitos del Sistema:**
```
- Python 3.11+
- PostgreSQL 12+
- RAM: 4GB mínimo, 8GB recomendado
- Disco: 10GB + espacio para documentos
- CPU: 2 cores mínimo, 4+ recomendado
```

### **Instalación:**
```bash
# 1. Clonar repositorio
git clone <repository>
cd SalesMind-agente-web-INDEXADORANDANGENTE

# 2. Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con credenciales

# 5. Inicializar base de datos
flask init-db

# 6. Agregar primer cliente
flask add-client "Mi Empresa" "chat_id" "carpeta_pdfs"

# 7. Ejecutar servidor
python app.py
```

### **Deployment en Producción:**
- Usar Gunicorn/uWSGI en lugar de Waitress
- Nginx como reverse proxy
- PostgreSQL con configuración optimizada
- Variables de entorno seguras
- Logs centralizados
- Monitoring con Prometheus/Grafana

---

## 🧪 **TESTING**

### **Scripts de Prueba:**
```bash
python test_rag.py          # Prueba sistema RAG básico
python test_multiidioma.py  # Prueba capacidades multiidioma
python test_completo.py     # Prueba integral del sistema
```

### **Casos de Prueba:**
- Indexación de documentos
- Búsqueda vectorial
- Respuestas multiidioma
- Aislamiento de clientes
- Manejo de errores

---

## 📈 **PRÓXIMAS VERSIONES**

### **v1.1.0 (Planeada):**
- Panel web de administración
- Métricas en tiempo real
- Soporte para DOCX/TXT
- Integración WhatsApp Business
- Caching inteligente

### **v1.2.0 (Futura):**
- Modelos de IA personalizables
- API pública completa
- Webhooks para integraciones
- Análisis de sentimientos
- Respuestas con attachments

---

**Versión:** 1.0.0  
**Fecha:** Octubre 2025  
**Status:** Producción Ready ✅