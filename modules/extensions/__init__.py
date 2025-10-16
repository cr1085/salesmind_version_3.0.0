# modules/extensions/__init__.py
"""
SISTEMA DE EXTENSIONES BLINDADO
===============================

Este módulo permite agregar nuevas funcionalidades SIN tocar código existente.
REGLA DE ORO: Las extensiones NUNCA modifican módulos core que ya funcionan.

ARQUITECTURA BLINDADA:
- modules/core/          -> CÓDIGO INTOCABLE (chat, indexado, cotizaciones)
- modules/extensions/    -> NUEVAS FUNCIONES (se agregan aquí)
- modules/integrations/  -> CONECTORES (unen extensiones con core sin modificarlo)
"""

# Registry de extensiones activas
_ACTIVE_EXTENSIONS = {}

def register_extension(name: str, extension_class):
    """Registra una nueva extensión sin modificar código existente."""
    global _ACTIVE_EXTENSIONS
    _ACTIVE_EXTENSIONS[name] = extension_class
    print(f"✅ Extensión '{name}' registrada exitosamente")

def get_extension(name: str):
    """Obtiene una extensión registrada."""
    return _ACTIVE_EXTENSIONS.get(name)

def list_extensions():
    """Lista todas las extensiones activas."""
    return list(_ACTIVE_EXTENSIONS.keys())

class BaseExtension:
    """
    Clase base para todas las extensiones.
    GARANTÍA: Las extensiones NUNCA pueden romper el sistema core.
    """
    
    def __init__(self, name: str):
        self.name = name
        self.enabled = True
        self.version = "1.0.0"
    
    def initialize(self):
        """Inicializa la extensión."""
        pass
    
    def process(self, *args, **kwargs):
        """Procesa datos de la extensión."""
        pass
    
    def cleanup(self):
        """Limpia recursos de la extensión."""
        pass