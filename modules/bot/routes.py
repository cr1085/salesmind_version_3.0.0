# Contenido para: modules/bot/routes.py

from flask import Blueprint, request
from config import Config
import telegram
import asyncio
from modules.assistant.core import get_commercial_response
from ..models import Conversation, Client
from .. import db

bot_bp = Blueprint('bot', __name__)
bot = telegram.Bot(token=Config.TELEGRAM_TOKEN)

# --- FUNCIÓN MIGRADA PARA GUARDAR MENSAJES EN POSTGRESQL ---
def log_message(chat_id, sender, message, client_id=None, platform='telegram', message_type='text'):
    """
    Guarda mensajes en PostgreSQL en lugar de SQLite.
    """
    try:
        # Si no se proporciona client_id, intentar encontrarlo por telegram_chat_id
        if not client_id:
            client = Client.query.filter_by(telegram_chat_id=str(chat_id)).first()
            if client:
                client_id = client.id
            else:
                print(f"ADVERTENCIA: No se encontró cliente para chat_id {chat_id}")
                return False
        
        # Crear nueva conversación en PostgreSQL
        conversation = Conversation(
            client_id=client_id,
            chat_id=str(chat_id),
            sender=sender,
            message_text=message,
            message_type=message_type,
            platform=platform
        )
        
        db.session.add(conversation)
        db.session.commit()
        
        print(f"✅ Mensaje guardado: {sender} -> {chat_id}")
        return True
        
    except Exception as e:
        print(f"❌ Error al guardar el mensaje en PostgreSQL: {e}")
        db.session.rollback()
        return False
# --- FIN DE LA FUNCIÓN MIGRADA ---

def run_async(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

@bot_bp.route('/telegram_webhook', methods=['POST'])
def telegram_webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    if update.message and update.message.text:
        chat_id = update.message.chat.id
        user_message = update.message.text

        # --- AÑADIMOS EL REGISTRO DE MENSAJES ---
        # 1. Guardamos el mensaje del usuario
        log_message(chat_id, 'user', user_message)

        # 2. Obtener cliente asociado al telegram chat
        client = Client.query.filter_by(telegram_chat_id=str(chat_id)).first()
        if not client:
            ai_message = "Lo siento, tu chat no está configurado correctamente. Contacta al administrador."
        else:
            # 3. Obtener respuesta de la IA usando PostgreSQL
            ai_message = get_commercial_response(user_message, client.id)
            
            # 4. Guardar ambos mensajes en PostgreSQL
            log_message(chat_id, 'user', user_message, client.id, 'telegram')
            log_message(chat_id, 'assistant', ai_message, client.id, 'telegram')
        # --- FIN DEL REGISTRO ---

        run_async(bot.send_message(chat_id=chat_id, text=ai_message))

    return "OK", 200