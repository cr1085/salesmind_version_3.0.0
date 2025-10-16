#!/usr/bin/env python3
# inspect_database.py
"""
Inspecciona la estructura actual de la base de datos PostgreSQL.
"""
import sys
import os

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules import create_app, db
from sqlalchemy import inspect, text

def inspect_database():
    """
    Inspecciona la estructura actual de la base de datos.
    """
    print("🔍 === INSPECCIONANDO BASE DE DATOS ===")
    
    app = create_app()
    
    with app.app_context():
        inspector = inspect(db.engine)
        
        # Obtener todas las tablas
        tables = inspector.get_table_names()
        print(f"\n📋 Tablas existentes ({len(tables)}):")
        
        for table in sorted(tables):
            print(f"\n🗂️  Tabla: {table}")
            
            # Obtener columnas de la tabla
            try:
                columns = inspector.get_columns(table)
                for col in columns:
                    nullable = "NULL" if col['nullable'] else "NOT NULL"
                    default = f"DEFAULT {col['default']}" if col['default'] else ""
                    print(f"   📊 {col['name']:<20} {str(col['type']):<15} {nullable:<8} {default}")
            except Exception as e:
                print(f"   ❌ Error obteniendo columnas: {e}")
        
        print("\n🎯 === VERIFICANDO MODELOS NECESARIOS ===")
        
        # Verificar tablas necesarias para la migración
        required_tables = ['client', 'conversations', 'documents', 'embeddings', 'faiss_indexes', 'query_logs']
        missing_tables = [t for t in required_tables if t not in tables]
        
        if missing_tables:
            print(f"\n❌ Tablas faltantes: {missing_tables}")
            print("\n🔧 Creando tablas faltantes...")
            
            try:
                # Forzar creación de todas las tablas
                db.create_all()
                
                # Verificar nuevamente
                inspector = inspect(db.engine)
                new_tables = inspector.get_table_names()
                created = set(new_tables) - set(tables)
                
                if created:
                    print(f"✅ Tablas creadas: {list(created)}")
                else:
                    print("⚠️ No se crearon nuevas tablas")
                    
            except Exception as e:
                print(f"❌ Error creando tablas: {e}")
        else:
            print("✅ Todas las tablas necesarias existen")

if __name__ == "__main__":
    inspect_database()