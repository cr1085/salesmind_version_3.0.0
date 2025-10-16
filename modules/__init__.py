# modules/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config, BASE_DIR
import os
import click
from flask_cors import CORS # <-- 1. IMPORTA LA LIBRERÍA
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

# from indexer import create_client_index  # Importación movida para evitar circular import

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    CORS(app) # <-- 2. INICIALIZA CORS CON TU APP

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)

    def create_database_if_not_exists():
        db_url = app.config['SQLALCHEMY_DATABASE_URI']
        engine = create_engine(db_url)
        if not database_exists(engine.url):
            create_database(engine.url)

    @app.cli.command("init-db")
    def init_db_command():
        with app.app_context():
            from .models import Client
            create_database_if_not_exists()
            db.create_all()
            click.echo("Base de datos inicializada.")

    @app.cli.command("add-client")
    @click.argument("name")
    @click.argument("telegram_id")
    @click.argument("pdfs_path")
    def add_client_command(name, telegram_id, pdfs_path):
        """Crea un nuevo cliente, indexa sus PDFs y lo guarda en PostgreSQL."""
        
        click.echo(f"🚀 Añadiendo nuevo cliente: {name}")
        click.echo(f"📁 Carpeta de PDFs: {pdfs_path}")
        
        from .models import Client
        
        with app.app_context():
            try:
                # 1. Crear cliente en PostgreSQL primero
                new_client = Client(
                    name=name,
                    telegram_chat_id=telegram_id,
                    index_path=None  # Se actualizará después de la indexación
                )
                db.session.add(new_client)
                db.session.flush()  # Para obtener el ID sin commit final
                
                client_id = new_client.id
                click.echo(f"👤 Cliente creado con ID: {client_id}")
                click.echo(f"🔑 Public ID: {new_client.public_id}")
                
                # 2. Crear índice usando PostgreSQL
                from indexer import create_client_index  # Import local para evitar circular
                success = create_client_index(pdfs_path, client_id)
                
                if not success:
                    db.session.rollback()
                    click.secho("❌ Falló la creación del índice. Abortando alta de cliente.", fg="red")
                    return
                
                # 3. Commit final si todo salió bien
                db.session.commit()
                
                click.secho(f"✅ ¡Cliente '{name}' añadido con éxito en PostgreSQL!", fg="green")
                click.echo(f"🔑 Su ID Público para el widget es: {new_client.public_id}")
                click.echo(f"📊 ID interno: {client_id}")
                
                # 4. Mostrar estadísticas finales
                try:
                    from indexer import get_client_index_info
                    info = get_client_index_info(client_id)
                except ImportError:
                    info = {"error": "No se pudo importar estadísticas"}
                
                if "error" not in info:
                    click.echo("\n📊 Estadísticas del cliente:")
                    click.echo(f"   📄 Documentos: {info['documents']['total_documents']}")
                    click.echo(f"   🧮 Embeddings: {info['vectors']['total_embeddings']}")
                    click.echo(f"   💾 Tamaño total: {info['vectors']['total_size_mb']} MB")
                    click.echo(f"   ✅ Estado: {info['status']}")
                
            except Exception as e:
                db.session.rollback()
                click.secho(f"❌ Error creando cliente: {e}", fg="red")
                import traceback
                traceback.print_exc()

    @app.cli.command()
    def list_clients():
        """Lista todos los clientes y sus estadísticas"""
        try:
            from .models import Client, Document, Embedding, FAISSIndex
            
            click.echo("📋 === LISTADO DE CLIENTES EN POSTGRESQL ===\n")
            
            clients = Client.query.all()
            
            if not clients:
                click.secho("❌ No hay clientes registrados", fg="yellow")
                return
            
            for client in clients:
                click.echo(f"👤 Cliente: {client.name}")
                click.echo(f"   🆔 ID Interno: {client.id}")
                click.echo(f"   🔑 Public ID: {client.public_id}")
                click.echo(f"   📱 Chat ID: {client.telegram_chat_id}")
                click.echo(f"   📅 Creado: {client.created_at}")
                
                # Contar documentos
                docs_count = Document.query.filter_by(client_id=client.id).count()
                
                # Contar embeddings
                embeddings_count = Embedding.query.filter_by(client_id=client.id).count()
                
                # Contar índices FAISS
                faiss_count = FAISSIndex.query.filter_by(client_id=client.id).count()
                
                click.echo(f"   📄 Documentos: {docs_count}")
                click.echo(f"   🧮 Embeddings: {embeddings_count}")
                click.echo(f"   🔧 Índices FAISS: {faiss_count}")
                
                # Verificar si tiene el mismo documento que otros
                if docs_count > 0:
                    client_docs = Document.query.filter_by(client_id=client.id).all()
                    for doc in client_docs:
                        # Contar cuántos clientes tienen el mismo documento
                        same_doc_count = Document.query.filter_by(content_hash=doc.content_hash).count()
                        if same_doc_count > 1:
                            click.echo(f"   🔄 Documento compartido: {doc.filename} (en {same_doc_count} clientes)")
                
                click.echo("")
                
            click.echo(f"📊 Total de clientes: {len(clients)}")
            
        except Exception as e:
            click.secho(f"❌ Error listando clientes: {e}", fg="red")

    @app.cli.command()
    @click.argument('client_id_or_name')
    def remove_client(client_id_or_name):
        """Elimina un cliente y todos sus datos asociados"""
        try:
            from .models import Client, Document, Embedding, FAISSIndex, Conversation
            
            # Buscar cliente por ID o nombre
            try:
                client_id = int(client_id_or_name)
                client = Client.query.get(client_id)
            except ValueError:
                client = Client.query.filter_by(name=client_id_or_name).first()
            
            if not client:
                click.secho(f"❌ Cliente no encontrado: {client_id_or_name}", fg="red")
                return
            
            click.echo(f"🗑️ Eliminando cliente: {client.name} (ID: {client.id})")
            
            # Contar datos antes de eliminar
            docs_count = Document.query.filter_by(client_id=client.id).count()
            embeddings_count = Embedding.query.filter_by(client_id=client.id).count()
            faiss_count = FAISSIndex.query.filter_by(client_id=client.id).count()
            conv_count = Conversation.query.filter_by(client_id=client.id).count()
            
            # Confirmar eliminación
            if not click.confirm(f"¿Estás seguro de eliminar el cliente '{client.name}' y todos sus datos?"):
                click.secho("❌ Operación cancelada", fg="yellow")
                return
            
            # Eliminar en orden (por las foreign keys)
            click.echo("🗑️ Eliminando embeddings...")
            Embedding.query.filter_by(client_id=client.id).delete()
            
            click.echo("🗑️ Eliminando índices FAISS...")
            FAISSIndex.query.filter_by(client_id=client.id).delete()
            
            click.echo("🗑️ Eliminando conversaciones...")
            Conversation.query.filter_by(client_id=client.id).delete()
            
            click.echo("🗑️ Eliminando query logs...")
            from .models import QueryLog
            QueryLog.query.filter_by(client_id=client.id).delete()
            
            click.echo("🗑️ Eliminando documentos...")
            Document.query.filter_by(client_id=client.id).delete()
            
            click.echo("🗑️ Eliminando cliente...")
            db.session.delete(client)
            
            db.session.commit()
            
            click.secho(f"✅ Cliente eliminado exitosamente", fg="green")
            click.echo(f"   📄 Documentos eliminados: {docs_count}")
            click.echo(f"   🧮 Embeddings eliminados: {embeddings_count}")
            click.echo(f"   🔧 Índices FAISS eliminados: {faiss_count}")
            click.echo(f"   💬 Conversaciones eliminadas: {conv_count}")
            
        except Exception as e:
            db.session.rollback()
            click.secho(f"❌ Error eliminando cliente: {e}", fg="red")
            import traceback
            traceback.print_exc()

    from .assistant.routes import assistant_bp
    app.register_blueprint(assistant_bp)
    
    # Registrar blueprint del admin del indexador
    from .indexer_admin import indexer_bp
    app.register_blueprint(indexer_bp)
    
    # 📥 RUTAS PARA SISTEMA DE DESCARGA V2 (SIN REFRESH)
    @app.route("/secure-download/<token>")
    def secure_download(token):
        """Descarga segura con token temporal"""
        from flask import send_file, abort, Response
        from .quote_system_v2 import quote_system_v2
        
        file_data = quote_system_v2.get_file_by_token(token)
        if not file_data:
            abort(404)
        
        try:
            response = send_file(
                file_data['filepath'],
                as_attachment=True,
                download_name=file_data['filename'],
                mimetype='application/pdf'
            )
            # Headers para evitar cache y refresh
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            return response
        except Exception as e:
            print(f"❌ Error en descarga segura: {e}")
            abort(500)
    
    @app.route("/download-quote/<filename>")  
    def download_quote_fallback(filename):
        """Descarga tradicional (fallback)"""
        from flask import send_from_directory, abort
        import os
        
        quotes_dir = os.path.join(app.instance_path, 'quotes')
        try:
            response = send_from_directory(
                quotes_dir, 
                filename, 
                as_attachment=True,
                mimetype='application/pdf'
            )
            # Headers anti-refresh
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache' 
            response.headers['Expires'] = '0'
            return response
        except Exception as e:
            print(f"❌ Error en descarga tradicional: {e}")
            abort(404)
    
    @app.route("/")
    def index():
        return "¡El servidor de SalesMind está en línea y funcionando correctamente!"

    return app