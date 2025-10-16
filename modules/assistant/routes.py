# modules/assistant/routes.py
from flask import Blueprint, request, jsonify
import requests
import os
import time

# --- Nuevas importaciones ---
# Importamos el "cerebro" de la IA desde core.py
from .core import get_commercial_response
# Importamos los modelos de la base de datos
from ..models import Client, Conversation, QueryLog
from .. import db
# Importamos la configuración para las claves API
from config import Config

assistant_bp = Blueprint('assistant', __name__)

# --- FUNCIÓN DE UTILIDAD PARA NOTIFICACIONES DE TELEGRAM ---
def send_telegram_notification(message, client_chat_id):
    """
    Envía un mensaje a un chat específico de Telegram.
    """
    token = Config.TELEGRAM_TOKEN
    
    if not token or not client_chat_id:
        print("ADVERTENCIA: Faltan variables de Telegram para enviar la notificación.")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": client_chat_id, "text": message}
    
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Error al enviar notificación a Telegram: {e}")

# --- EL NUEVO ENDPOINT PRINCIPAL PARA EL CHAT WEB ---
@assistant_bp.route("/chat-api", methods=['POST'])
def chat_api():
    """
    Recibe los mensajes desde el widget de chat web.
    """
    data = request.get_json()
    user_message = data.get('message')
    client_public_id = data.get('clientId') # El widget enviará el ID público del cliente

    if not all([user_message, client_public_id]):
        return jsonify({"error": "Faltan datos en la petición (message o clientId)"}), 400

    # 1. Buscamos al cliente en la base de datos usando su ID público
    client = Client.query.filter_by(public_id=client_public_id).first()

    if not client:
        return jsonify({"error": "Cliente no válido o no encontrado."}), 403

    # --- NUEVA LÓGICA CON POSTGRESQL ---
    start_time = time.time()
    
    try:
        # 1. Registrar mensaje del usuario en PostgreSQL
        user_conversation = Conversation(
            client_id=client.id,
            chat_id=f"web_{client.public_id}",  # ID único para chat web
            sender='user',
            message_text=user_message,
            platform='web',
            message_type='text'
        )
        db.session.add(user_conversation)
        db.session.flush()  # Para obtener el ID sin hacer commit
        
        # 2. Obtener respuesta de la IA (ahora desde PostgreSQL)
        ai_response = get_commercial_response(user_message, client.public_id)  # Pasamos public_id como espera la función
        
        # 3. Registrar respuesta del bot en PostgreSQL
        bot_conversation = Conversation(
            client_id=client.id,
            chat_id=f"web_{client.public_id}",
            sender='assistant',
            message_text=ai_response,
            platform='web',
            message_type='text'
        )
        db.session.add(bot_conversation)
        
        # 4. Calcular tiempo de respuesta
        response_time = time.time() - start_time
        
        # 5. Registrar la consulta completa en QueryLog
        query_log = QueryLog(
            client_id=client.id,
            conversation_id=user_conversation.id,
            question=user_message,
            answer=ai_response,
            response_time=response_time,
            model_used='gemini-1.5-flash-latest',  # Ajustar según configuración
            retrieved_chunks=3  # Ajustar según lo que devuelva RAG
        )
        db.session.add(query_log)
        
        # 6. Commit todas las operaciones
        db.session.commit()
        
        print(f"✅ Conversación guardada en PostgreSQL - Cliente: {client.name}")
        
    except Exception as e:
        print(f"❌ Error al guardar conversación: {e}")
        db.session.rollback()
        # Aún devolvemos la respuesta aunque falle el logging
        ai_response = "Lo siento, ocurrió un error procesando tu consulta."
    
    # 7. Enviar notificación a Telegram (opcional)
    if client.telegram_chat_id:
        notification_message = (
            f"🤖 Nuevo lead de '{client.name}'\n"
            f"----------------------------------\n"
            f"**Pregunta:** {user_message}\n"
            f"**Respuesta:** {ai_response}"
        )
        send_telegram_notification(notification_message, client.telegram_chat_id)

    # 8. Devolver respuesta al widget de chat
    return jsonify({
        "reply": ai_response,
        "timestamp": user_conversation.timestamp.isoformat() if 'user_conversation' in locals() else None,
        "client_name": client.name
    })

# --- RUTA PARA DESCARGAR COTIZACIONES PDF ---
@assistant_bp.route("/download-quote/<filename>", methods=['GET'])
def download_quote(filename):
    """
    Permite descargar cotizaciones PDF generadas
    """
    try:
        from flask import send_file
        import os
        
        # Directorio de cotizaciones
        quotes_dir = "instance/quotes"
        file_path = os.path.join(quotes_dir, filename)
        
        # Verificar que el archivo existe y es un PDF
        if not os.path.exists(file_path) or not filename.endswith('.pdf'):
            return jsonify({"error": "Archivo no encontrado"}), 404
        
        # Enviar archivo
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        print(f"❌ Error descargando cotización: {e}")
        return jsonify({"error": "Error al descargar archivo"}), 500