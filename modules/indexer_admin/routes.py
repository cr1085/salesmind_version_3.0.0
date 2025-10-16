# modules/indexer_admin/routes.py
import os
import uuid
import json
from datetime import datetime
from flask import render_template, request, jsonify, flash, redirect, url_for, current_app
from werkzeug.utils import secure_filename
from . import indexer_bp
from .. import db
from ..models import Client, Conversation, QueryLog, Document
import subprocess
import sys

ALLOWED_EXTENSIONS = {'pdf', 'txt', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@indexer_bp.route('/')
def dashboard():
    """Panel principal del administrador de indexación"""
    try:
        # Obtener estadísticas generales
        total_clients = Client.query.count()
        clients = Client.query.order_by(Client.created_at.desc()).limit(10).all()
        
        # Obtener información del sistema
        system_info = {
            'python_version': sys.version,
            'total_clients': total_clients,
            'database_connected': True,
            'indexer_status': 'operational'
        }
        
        return render_template('indexer_admin/dashboard.html', 
                             clients=clients, 
                             system_info=system_info)
    except Exception as e:
        current_app.logger.error(f"Error en dashboard: {str(e)}")
        system_info = {
            'database_connected': False,
            'error': str(e)
        }
        return render_template('indexer_admin/dashboard.html', 
                             clients=[], 
                             system_info=system_info)

@indexer_bp.route('/clients')
def list_clients():
    """Lista todos los clientes con información detallada"""
    try:
        clients = Client.query.order_by(Client.created_at.desc()).all()
        
        # Obtener estadísticas de cada cliente
        clients_data = []
        for client in clients:
            try:
                # Importación local para evitar errores circulares
                import indexer
                info = indexer.get_client_index_info(client.id)
                client_data = {
                    'client': client,
                    'stats': info if 'error' not in info else None,
                    'error': info.get('error') if 'error' in info else None
                }
            except ImportError as e:
                client_data = {
                    'client': client,
                    'stats': None,
                    'error': f"Error importando indexer: {str(e)}"
                }
            except Exception as e:
                client_data = {
                    'client': client,
                    'stats': None,
                    'error': str(e)
                }
            clients_data.append(client_data)
        
        return render_template('indexer_admin/clients.html', clients_data=clients_data)
    except Exception as e:
        current_app.logger.error(f"Error listando clientes: {str(e)}")
        flash(f'Error al obtener la lista de clientes: {str(e)}', 'error')
        return redirect(url_for('indexer_admin.dashboard'))

@indexer_bp.route('/client/<int:client_id>')
def client_detail(client_id):
    """Detalles específicos de un cliente"""
    try:
        client = Client.query.get_or_404(client_id)
        
        # Obtener información completa del cliente
        try:
            import indexer
            stats = indexer.get_client_index_info(client_id)
            documents = indexer.get_client_documents(client_id)
        except ImportError as e:
            stats = {'error': f'Error importando indexer: {str(e)}'}
            documents = []
        except Exception as e:
            stats = {'error': str(e)}
            documents = []
        
        return render_template('indexer_admin/client_detail.html', 
                             client=client, 
                             stats=stats, 
                             documents=documents)
    except Exception as e:
        current_app.logger.error(f"Error obteniendo detalles del cliente {client_id}: {str(e)}")
        flash(f'Error al obtener detalles del cliente: {str(e)}', 'error')
        return redirect(url_for('indexer_admin.list_clients'))

@indexer_bp.route('/add-client', methods=['GET', 'POST'])
def add_client():
    """Formulario para agregar nuevo cliente"""
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            telegram_id = request.form.get('telegram_id', '').strip()
            
            if not name:
                flash('El nombre del cliente es requerido', 'error')
                return render_template('indexer_admin/add_client.html')
            
            # Verificar si el cliente ya existe
            existing_client = Client.query.filter_by(name=name).first()
            if existing_client:
                flash(f'Ya existe un cliente con el nombre "{name}"', 'error')
                return render_template('indexer_admin/add_client.html')
            
            # Crear el cliente
            new_client = Client(
                name=name,
                telegram_chat_id=telegram_id or None,
                index_path='postgresql_storage'
            )
            
            db.session.add(new_client)
            db.session.flush()  # Para obtener el ID
            
            client_id = new_client.id
            
            # Si se subieron archivos, procesarlos
            uploaded_files = request.files.getlist('documents')
            processed_files = 0
            
            if uploaded_files and uploaded_files[0].filename:
                # Crear directorio temporal para los archivos
                temp_dir = os.path.join(current_app.instance_path, 'temp_uploads', str(uuid.uuid4()))
                os.makedirs(temp_dir, exist_ok=True)
                
                try:
                    for file in uploaded_files:
                        if file and allowed_file(file.filename):
                            filename = secure_filename(file.filename)
                            file_path = os.path.join(temp_dir, filename)
                            file.save(file_path)
                            processed_files += 1
                    
                    # Crear índice con los archivos subidos
                    if processed_files > 0:
                        from indexer import create_client_index
                        success = create_client_index(temp_dir, client_id)
                        
                        if not success:
                            # Limpiar archivos temporales
                            import shutil
                            shutil.rmtree(temp_dir, ignore_errors=True)
                            
                            db.session.rollback()
                            flash('Error al procesar los documentos. Cliente no creado.', 'error')
                            return render_template('indexer_admin/add_client.html')
                    
                    # Limpiar archivos temporales
                    import shutil
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    
                except Exception as e:
                    # Limpiar en caso de error
                    import shutil
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    raise e
            
            db.session.commit()
            
            flash(f'Cliente "{name}" creado exitosamente. ID público: {new_client.public_id}', 'success')
            return redirect(url_for('indexer_admin.client_detail', client_id=client_id))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creando cliente: {str(e)}")
            flash(f'Error al crear el cliente: {str(e)}', 'error')
    
    return render_template('indexer_admin/add_client.html')

@indexer_bp.route('/upload-documents/<int:client_id>', methods=['POST'])
def upload_documents(client_id):
    """Subir documentos adicionales a un cliente existente"""
    try:
        client = Client.query.get_or_404(client_id)
        
        uploaded_files = request.files.getlist('documents')
        if not uploaded_files or not uploaded_files[0].filename:
            return jsonify({'success': False, 'message': 'No se seleccionaron archivos'})
        
        # Crear directorio temporal
        temp_dir = os.path.join(current_app.instance_path, 'temp_uploads', str(uuid.uuid4()))
        os.makedirs(temp_dir, exist_ok=True)
        
        processed_files = 0
        
        try:
            for file in uploaded_files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(temp_dir, filename)
                    file.save(file_path)
                    processed_files += 1
            
            if processed_files == 0:
                return jsonify({'success': False, 'message': 'No se encontraron archivos válidos'})
            
            # Agregar documentos al cliente existente con procesamiento automático completo
            from modules.document_manager import DocumentManager
            from modules.vector_manager import VectorManager
            
            doc_manager = DocumentManager()
            vector_manager = VectorManager()
            
            added_documents = []
            for filename in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, filename)
                if os.path.isfile(file_path):
                    # 1. Agregar documento y extraer texto
                    document = doc_manager.add_document_from_file(client_id, file_path)
                    if document:
                        added_documents.append(document)
                        print(f"✅ Documento agregado: {document.filename}")
                        
                        # 2. Crear embeddings automáticamente
                        embeddings = vector_manager.create_embeddings_from_document(document.id)
                        print(f"✅ {len(embeddings)} embeddings creados para {document.filename}")
            
            # 3. Recrear índice FAISS con todos los embeddings del cliente
            if added_documents:
                faiss_index = vector_manager.create_faiss_index_for_client(client_id)
                if faiss_index:
                    print(f"✅ Índice FAISS actualizado con {faiss_index.total_vectors} vectores")
                
            added_count = len(added_documents)
            
            # Limpiar archivos temporales
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            return jsonify({
                'success': True, 
                'message': f'{added_count} documentos agregados exitosamente'
            })
            
        except Exception as e:
            # Limpiar en caso de error
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise e
            
    except Exception as e:
        current_app.logger.error(f"Error subiendo documentos para cliente {client_id}: {str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@indexer_bp.route('/reindex-client/<int:client_id>', methods=['POST'])
def reindex_client(client_id):
    """Re-indexar todos los documentos de un cliente"""
    try:
        client = Client.query.get_or_404(client_id)
        
        from modules.vector_manager import VectorManager
        vector_manager = VectorManager()
        
        # Re-crear índice FAISS
        success = vector_manager.create_faiss_index_for_client(client_id)
        
        if success:
            return jsonify({
                'success': True, 
                'message': f'Cliente "{client.name}" re-indexado exitosamente'
            })
        else:
            return jsonify({
                'success': False, 
                'message': 'Error durante la re-indexación'
            })
            
    except Exception as e:
        current_app.logger.error(f"Error re-indexando cliente {client_id}: {str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@indexer_bp.route('/system-status')
def system_status():
    """Estado del sistema en tiempo real"""
    try:
        # Verificar conexión a base de datos
        db_connected = True
        try:
            db.session.execute('SELECT 1')
        except Exception:
            db_connected = False
        
        # Estadísticas generales
        total_clients = Client.query.count() if db_connected else 0
        
        # Información del sistema
        import psutil
        system_info = {
            'database_connected': db_connected,
            'total_clients': total_clients,
            'python_version': sys.version.split()[0],
            'memory_usage': f"{psutil.virtual_memory().percent}%",
            'disk_usage': f"{psutil.disk_usage('/').percent}%",
            'cpu_usage': f"{psutil.cpu_percent()}%",
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return jsonify(system_info)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'database_connected': False,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

@indexer_bp.route('/api/test-client/<client_public_id>')
def test_client_api(client_public_id):
    """Probar la API de un cliente específico"""
    try:
        from modules.assistant.core import get_commercial_response
        
        # Pregunta de prueba
        test_question = "¿Qué información tienes disponible?"
        
        response = get_commercial_response(test_question, client_public_id)
        
        return jsonify({
            'success': True,
            'question': test_question,
            'response': response,
            'client_id': client_public_id,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'client_id': client_public_id,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

@indexer_bp.route('/logs')
def view_logs():
    """Ver logs del sistema"""
    try:
        # Obtener logs recientes de conversaciones de forma segura
        recent_conversations = []
        recent_queries = []
        
        try:
            recent_conversations = Conversation.query.order_by(
                Conversation.timestamp.desc()
            ).limit(50).all()
        except Exception as conv_error:
            current_app.logger.warning(f"Error cargando conversaciones: {conv_error}")
        
        try:
            recent_queries = QueryLog.query.order_by(
                QueryLog.timestamp.desc()
            ).limit(50).all()
        except Exception as query_error:
            current_app.logger.warning(f"Error cargando queries: {query_error}")
        
        return render_template('indexer_admin/logs.html', 
                             conversations=recent_conversations,
                             queries=recent_queries)
        
    except Exception as e:
        current_app.logger.error(f"Error obteniendo logs: {str(e)}")
        # Devolver página con listas vacías en caso de error
        return render_template('indexer_admin/logs.html', 
                             conversations=[],
                             queries=[])