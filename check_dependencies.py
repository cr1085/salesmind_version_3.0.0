#!/usr/bin/env python3
# check_dependencies.py
"""
Verifica que todas las dependencias estén correctamente instaladas.
"""
import sys
import importlib

def check_dependency(package_name, import_name=None, version_attr=None):
    """
    Verifica si un paquete está instalado y funcionando.
    
    Args:
        package_name: Nombre del paquete para mostrar
        import_name: Nombre para importar (si es diferente)
        version_attr: Atributo para obtener la versión
    """
    if import_name is None:
        import_name = package_name.replace('-', '_')
    
    try:
        module = importlib.import_module(import_name)
        
        version = "N/A"
        if version_attr and hasattr(module, version_attr):
            version = getattr(module, version_attr)
        elif hasattr(module, '__version__'):
            version = module.__version__
        
        print(f"✅ {package_name:<25} - {version}")
        return True
        
    except ImportError as e:
        print(f"❌ {package_name:<25} - ERROR: {e}")
        return False

def main():
    """Verifica todas las dependencias del sistema."""
    print("🔍 === VERIFICACIÓN DE DEPENDENCIAS ===\n")
    
    dependencies = [
        # Core Framework
        ("Flask", "flask"),
        ("Flask-SQLAlchemy", "flask_sqlalchemy"),
        ("Flask-CORS", "flask_cors"),
        ("SQLAlchemy", "sqlalchemy"),
        ("Waitress", "waitress"),
        
        # Database
        ("psycopg2-binary", "psycopg2"),
        ("sqlalchemy-utils", "sqlalchemy_utils"),
        
        # Configuration
        ("python-dotenv", "dotenv"),
        ("nest-asyncio", "nest_asyncio"),
        
        # HTTP & Requests
        ("requests", "requests"),
        
        # AI & Embeddings
        ("langchain", "langchain"),
        ("langchain-community", "langchain_community"),
        ("langchain-google-genai", "langchain_google_genai"),
        ("google-generativeai", "google.generativeai"),
        
        # Vector Search
        ("faiss-cpu", "faiss"),
        ("numpy", "numpy"),
        
        # Document Processing
        ("PyMuPDF", "fitz"),
        
        # Telegram
        ("python-telegram-bot", "telegram"),
        
        # Text Processing
        ("sentence-transformers", "sentence_transformers"),
        
        # Additional
        ("twilio", "twilio"),
    ]
    
    success_count = 0
    total_count = len(dependencies)
    
    for package_name, import_name in dependencies:
        if check_dependency(package_name, import_name):
            success_count += 1
    
    print(f"\n📊 RESUMEN: {success_count}/{total_count} dependencias instaladas")
    
    if success_count == total_count:
        print("🎉 ¡Todas las dependencias están correctamente instaladas!")
        
        # Test crítico adicional
        print("\n🧪 === TESTS ADICIONALES ===")
        
        # Test PostgreSQL connection
        try:
            import psycopg2
            print("✅ psycopg2 disponible para PostgreSQL")
        except Exception as e:
            print(f"❌ Error con psycopg2: {e}")
        
        # Test FAISS
        try:
            import faiss
            import numpy as np
            
            # Test básico de FAISS
            dimension = 128
            index = faiss.IndexFlatL2(dimension)
            vectors = np.random.random((10, dimension)).astype('float32')
            index.add(vectors)
            
            if index.ntotal == 10:
                print("✅ FAISS funcionando correctamente")
            else:
                print("❌ FAISS no está funcionando correctamente")
                
        except Exception as e:
            print(f"❌ Error con FAISS: {e}")
        
        # Test pickle nativo
        try:
            import pickle
            import numpy as np
            
            test_array = np.array([1.0, 2.0, 3.0], dtype=np.float32)
            serialized = pickle.dumps(test_array, protocol=pickle.HIGHEST_PROTOCOL)
            deserialized = pickle.loads(serialized)
            
            if np.array_equal(test_array, deserialized):
                print("✅ Serialización pickle funcionando")
            else:
                print("❌ Problema con serialización pickle")
                
        except Exception as e:
            print(f"❌ Error con pickle: {e}")
        
        print("\n🚀 Sistema listo para ejecutar!")
        
    else:
        print(f"\n❌ Faltan {total_count - success_count} dependencias")
        print("\nPara instalar las faltantes, ejecuta:")
        print("pip install -r requirements.txt")
        
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())