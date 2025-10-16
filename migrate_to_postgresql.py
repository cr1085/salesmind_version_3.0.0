#!/usr/bin/env python3
# migrate_to_postgresql.py
"""
Script de migración para mover datos existentes desde archivos y SQLite a PostgreSQL.
"""
import os
import sys
import json
import sqlite3
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules import create_app, db
from modules.models import Client, Conversation, Document, Embedding, FAISSIndex
from modules.document_manager import DocumentManager
from modules.vector_manager import VectorManager
from config import Config, BASE_DIR

def migrate_existing_clients():
    """
    Migra clientes existentes desde client_indexes/ a PostgreSQL.
    """
    print("🔄 === MIGRANDO CLIENTES EXISTENTES ===")
    
    client_indexes_path = os.path.join(BASE_DIR, 'client_indexes')
    
    if not os.path.exists(client_indexes_path):
        print("⚠️ No se encontró carpeta client_indexes/")
        return
    
    clients_migrated = 0
    
    for client_folder in os.listdir(client_indexes_path):
        client_path = os.path.join(client_indexes_path, client_folder)
        
        if not os.path.isdir(client_path):
            continue
        
        print(f"\n📁 Procesando cliente: {client_folder}")
        
        # Buscar si ya existe en PostgreSQL
        existing_client = Client.query.filter_by(name=client_folder).first()
        if existing_client:
            print(f"   ⏭️ Cliente ya existe en PostgreSQL, saltando...")
            continue
        
        # Crear cliente en PostgreSQL
        client = Client(
            name=client_folder.replace('_', ' ').title(),  # "cafe_del_sol" -> "Cafe Del Sol"
            telegram_chat_id=None,  # Se puede actualizar manualmente después
            index_path=client_path  # Mantener referencia temporal
        )
        
        db.session.add(client)
        db.session.flush()  # Obtener ID
        
        print(f"   ✅ Cliente creado con ID: {client.id}")
        
        # Buscar PDFs originales para migrar
        pdf_folders = [
            f"pdfs_{client_folder}",
            f"pdfs{client_folder}",
            client_folder,
        ]
        
        pdf_path = None
        for folder in pdf_folders:
            potential_path = os.path.join(BASE_DIR, folder)
            if os.path.exists(potential_path):
                pdf_path = potential_path
                break
        
        if pdf_path and os.listdir(pdf_path):
            print(f"   📄 Migrando PDFs desde: {pdf_path}")
            doc_manager = DocumentManager()
            documents = doc_manager.add_documents_from_folder(client.id, pdf_path)
            print(f"   ✅ {len(documents)} documentos migrados")
            
            # Crear embeddings y índice
            if documents:
                print(f"   🧮 Generando embeddings...")
                vector_manager = VectorManager()
                total_embeddings = 0
                
                for doc in documents:
                    embeddings = vector_manager.create_embeddings_from_document(doc.id)
                    total_embeddings += len(embeddings)
                
                print(f"   ✅ {total_embeddings} embeddings creados")
                
                # Crear índice FAISS
                faiss_index = vector_manager.create_faiss_index_for_client(client.id)
                if faiss_index:
                    print(f"   🔧 Índice FAISS creado")
                
        clients_migrated += 1
    
    db.session.commit()
    print(f"\n🎉 Migración completada: {clients_migrated} clientes migrados")


def migrate_conversations_from_sqlite():
    """
    Migra conversaciones desde SQLite a PostgreSQL.
    """
    print("\n💬 === MIGRANDO CONVERSACIONES DESDE SQLITE ===")
    
    sqlite_path = getattr(Config, 'DATABASE_PATH', 'instance/legal_db.db')
    
    if not os.path.exists(sqlite_path):
        print("⚠️ Base de datos SQLite no encontrada")
        return
    
    try:
        # Conectar a SQLite
        conn = sqlite3.connect(sqlite_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Obtener conversaciones
        cursor.execute("SELECT * FROM conversations ORDER BY timestamp ASC")
        conversations = cursor.fetchall()
        conn.close()
        
        print(f"📊 Encontradas {len(conversations)} conversaciones en SQLite")
        
        conversations_migrated = 0
        
        for conv in conversations:
            # Buscar cliente por chat_id de Telegram
            client = Client.query.filter_by(telegram_chat_id=str(conv['chat_id'])).first()
            
            if not client:
                print(f"⚠️ No se encontró cliente para chat_id: {conv['chat_id']}")
                continue
            
            # Crear conversación en PostgreSQL
            new_conv = Conversation(
                client_id=client.id,
                chat_id=str(conv['chat_id']),
                sender=conv['sender'],
                message_text=conv['message_text'],
                timestamp=conv['timestamp'],
                platform='telegram',
                message_type='text'
            )
            
            db.session.add(new_conv)
            conversations_migrated += 1
        
        db.session.commit()
        print(f"✅ {conversations_migrated} conversaciones migradas a PostgreSQL")
        
    except Exception as e:
        print(f"❌ Error migrando conversaciones: {e}")
        db.session.rollback()


def generate_migration_report():
    """
    Genera un reporte del estado post-migración.
    """
    print("\n📊 === REPORTE DE MIGRACIÓN ===")
    
    clients = Client.query.all()
    print(f"👥 Clientes en PostgreSQL: {len(clients)}")
    
    for client in clients:
        print(f"\n👤 Cliente: {client.name}")
        print(f"   🔑 Public ID: {client.public_id}")
        print(f"   📱 Telegram: {client.telegram_chat_id or 'No configurado'}")
        
        # Estadísticas de documentos
        doc_manager = DocumentManager()
        doc_stats = doc_manager.get_documents_stats(client.id)
        print(f"   📄 Documentos: {doc_stats['total_documents']}")
        print(f"   💾 Tamaño: {doc_stats['total_size_mb']} MB")
        
        # Estadísticas de vectores
        vector_manager = VectorManager()
        vector_stats = vector_manager.get_client_vector_stats(client.id)
        print(f"   🧮 Embeddings: {vector_stats['total_embeddings']}")
        print(f"   🔧 Índices activos: {vector_stats['active_indexes']}")
        
        # Conversaciones
        conversations = Conversation.query.filter_by(client_id=client.id).count()
        print(f"   💬 Conversaciones: {conversations}")


def main():
    """
    Función principal de migración.
    """
    print("🚀 === MIGRACIÓN A POSTGRESQL ===")
    print("Este script migra datos existentes desde archivos y SQLite a PostgreSQL")
    
    # Crear aplicación Flask
    app = create_app()
    
    with app.app_context():
        # Verificar conexión a PostgreSQL
        try:
            db.engine.execute('SELECT 1')
            print("✅ Conexión a PostgreSQL establecida")
        except Exception as e:
            print(f"❌ Error conectando a PostgreSQL: {e}")
            return
        
        # Crear tablas si no existen
        print("📋 Asegurando que las tablas existan...")
        db.create_all()
        
        # Ejecutar migraciones
        try:
            migrate_existing_clients()
            migrate_conversations_from_sqlite()
            generate_migration_report()
            
            print("\n🎉 ¡MIGRACIÓN COMPLETADA EXITOSAMENTE!")
            print("\n📝 Próximos pasos:")
            print("   1. Verificar que todos los clientes estén correctamente migrados")
            print("   2. Actualizar telegram_chat_id de los clientes si es necesario")
            print("   3. Probar que las consultas funcionen correctamente")
            print("   4. Considerar hacer backup de los archivos originales")
            
        except Exception as e:
            print(f"\n❌ Error durante la migración: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()