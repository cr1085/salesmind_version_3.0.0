#!/usr/bin/env python3
# fix_database_schema.py
"""
Script para arreglar el esquema de la base de datos después de la migración.
"""
import sys
import os

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules import create_app, db
from sqlalchemy import text

def fix_client_table():
    """
    Hace que la columna index_path sea nullable y añade un valor por defecto.
    """
    print("🔧 === ARREGLANDO ESQUEMA DE BASE DE DATOS ===")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Hacer que index_path sea nullable
            print("📝 Actualizando columna index_path...")
            
            # Para PostgreSQL, necesitamos usar ALTER TABLE (SQLAlchemy 2.0 syntax)
            with db.engine.connect() as conn:
                conn.execute(text("""
                    ALTER TABLE client 
                    ALTER COLUMN index_path DROP NOT NULL;
                """))
                
                # Establecer valores por defecto para registros existentes con NULL
                conn.execute(text("""
                    UPDATE client 
                    SET index_path = 'postgresql_storage' 
                    WHERE index_path IS NULL;
                """))
                
                conn.commit()
            
            print("✅ Esquema actualizado correctamente")
            
            # Mostrar clientes existentes
            with db.engine.connect() as conn:
                result = conn.execute(text("SELECT id, name, public_id, index_path FROM client ORDER BY id"))
                clients = result.fetchall()
            
            if clients:
                print(f"\n👥 Clientes existentes ({len(clients)}):")
                for client in clients:
                    print(f"   ID: {client[0]} | Nombre: {client[1]} | Index: {client[3] or 'NULL'}")
            else:
                print("\n👥 No hay clientes en la base de datos")
            
        except Exception as e:
            print(f"❌ Error actualizando esquema: {e}")
            return False
        
        return True

if __name__ == "__main__":
    if fix_client_table():
        print("\n🎉 ¡Esquema arreglado exitosamente!")
    else:
        print("\n❌ Error arreglando el esquema")
        sys.exit(1)