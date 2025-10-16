#!/usr/bin/env python3
"""
Script para corregir las restricciones de la base de datos PostgreSQL
- Elimina la restricción unique del content_hash
- Agrega la restricción compuesta (client_id, content_hash)
"""

import os
import sys
from sqlalchemy import create_engine, text
from config import Config

def fix_database_constraints():
    """Corrige las restricciones de la tabla salesmind_documents"""
    
    try:
        # Crear conexión a PostgreSQL
        config = Config()
        engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
        
        print("🔧 Conectando a PostgreSQL...")
        
        with engine.begin() as conn:
            # 1. Verificar restricciones actuales
            print("📋 Verificando restricciones actuales...")
            result = conn.execute(text("""
                SELECT conname, contype, pg_get_constraintdef(oid) as definition
                FROM pg_constraint 
                WHERE conrelid = 'salesmind_documents'::regclass
                AND contype = 'u'
            """))
            
            constraints = result.fetchall()
            print(f"Restricciones encontradas: {len(constraints)}")
            
            for constraint in constraints:
                print(f"  - {constraint.conname}: {constraint.definition}")
            
            # 2. Eliminar restricción unique del content_hash si existe
            print("\n🗑️ Eliminando restricción unique del content_hash...")
            try:
                conn.execute(text("""
                    ALTER TABLE salesmind_documents 
                    DROP CONSTRAINT IF EXISTS salesmind_documents_content_hash_key
                """))
                print("✅ Restricción unique del content_hash eliminada")
            except Exception as e:
                print(f"⚠️ No se pudo eliminar restricción: {e}")
            
            # 3. Agregar nueva restricción compuesta
            print("\n➕ Agregando restricción compuesta (client_id, content_hash)...")
            try:
                conn.execute(text("""
                    ALTER TABLE salesmind_documents 
                    ADD CONSTRAINT unique_client_document 
                    UNIQUE (client_id, content_hash)
                """))
                print("✅ Restricción compuesta agregada exitosamente")
            except Exception as e:
                print(f"⚠️ Error al agregar restricción compuesta: {e}")
            
            # 4. Verificar restricciones finales
            print("\n📋 Verificando restricciones finales...")
            result = conn.execute(text("""
                SELECT conname, contype, pg_get_constraintdef(oid) as definition
                FROM pg_constraint 
                WHERE conrelid = 'salesmind_documents'::regclass
                AND contype = 'u'
            """))
            
            final_constraints = result.fetchall()
            print(f"Restricciones finales: {len(final_constraints)}")
            
            for constraint in final_constraints:
                print(f"  - {constraint.conname}: {constraint.definition}")
        
        print("\n🎉 ¡Base de datos corregida exitosamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error al corregir base de datos: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando corrección de base de datos...")
    success = fix_database_constraints()
    
    if success:
        print("\n✨ La base de datos está lista para múltiples clientes con documentos compartidos")
        print("💼 Ahora puedes vender el sistema a más de 100 empresas sin problemas")
    else:
        print("\n❌ Falló la corrección. Revisar errores arriba.")
        sys.exit(1)