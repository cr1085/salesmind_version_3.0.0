from collections import defaultdict
from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required


main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=current_user.username)


@main_bp.route('/manual')
@login_required
def manual():
    return render_template('manual.html')


@main_bp.route('/conversations')
@login_required
def conversations_dashboard():
    """
    Dashboard de conversaciones - MIGRADO A POSTGRESQL
    """
    from ..models import Conversation, Client
    
    # Obtener todas las conversaciones desde PostgreSQL
    conversations_query = Conversation.query.join(Client).order_by(Conversation.timestamp.asc()).all()
    
    # Agrupar por cliente y chat_id
    conversations = defaultdict(lambda: {
        'client_name': '',
        'messages': []
    })
    
    for conv in conversations_query:
        key = f"{conv.client.name}_{conv.chat_id}"
        conversations[key]['client_name'] = conv.client.name
        conversations[key]['messages'].append({
            'id': conv.id,
            'chat_id': conv.chat_id,
            'sender': conv.sender,
            'message_text': conv.message_text,
            'timestamp': conv.timestamp,
            'platform': conv.platform,
            'message_type': conv.message_type
        })
        
    return render_template('conversations_dashboard.html', conversations=conversations)
# --- FIN DE LA NUEVA RUTA ---