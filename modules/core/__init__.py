# modules/core/__init__.py
"""
MÓDULOS CORE - CÓDIGO INTOCABLE
===============================

ADVERTENCIA: ¡NUNCA MODIFIQUES ESTOS MÓDULOS DIRECTAMENTE!
           Si necesitas nuevas funciones, usa el sistema de extensiones.

MÓDULOS CORE PROTEGIDOS:
- assistant/core.py      -> Lógica RAG y multilenguaje  
- models.py              -> Modelos de base de datos
- vector_manager.py      -> Gestión de embeddings y FAISS
- document_manager.py    -> Procesamiento de documentos
- quote_generator.py     -> Generación de cotizaciones PDF
- indexer_admin/routes.py -> Panel administrativo

REGLAS DE ESCALABILIDAD:
1. NUNCA modifiques archivos en modules/core/
2. Usa modules/extensions/ para nuevas funciones
3. Usa modules/integrations/ para conectar extensiones con core
4. Usa hooks y events para extender funcionalidad

GARANTÍA: Siguiendo estas reglas, el sistema NUNCA se romperá.
"""

# Lista de módulos protegidos
PROTECTED_MODULES = [
    'assistant.core',
    'models', 
    'vector_manager',
    'document_manager',
    'quote_generator',
    'indexer_admin.routes'
]

def is_core_module(module_name: str) -> bool:
    """Verifica si un módulo es parte del core protegido."""
    return any(protected in module_name for protected in PROTECTED_MODULES)

class CoreProtectionError(Exception):
    """Error lanzado cuando se intenta modificar módulos core."""
    pass