"""
🧪 SERVIDOR DE PRUEBA PARA EL WIDGET
Solo para testing - no toca el sistema principal
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import time
import random

app = Flask(__name__)
CORS(app)

@app.route('/chat-api', methods=['POST'])
def chat_test():
    try:
        data = request.json
        message = data.get('message', '')
        client_id = data.get('clientId', 'unknown')
        
        # Simular tiempo de procesamiento
        time.sleep(1)
        
        # Respuestas de prueba
        if 'cotiz' in message.lower() or 'precio' in message.lower():
            reply = f"""¡Perfecto! He preparado una cotización personalizada para ti.

**Cotización - {client_id.upper()}**

📋 **Productos sugeridos:**
- Solución Premium: $2,500 USD
- Implementación: $800 USD  
- Soporte anual: $600 USD

💰 **Total estimado: $3,900 USD**

[Descargar Cotización Completa](http://localhost:5001/download-test.pdf)

¿Te gustaría que ajustemos algún aspecto de esta propuesta?"""
        
        elif 'hola' in message.lower():
            reply = f"""¡Hola! 👋 Soy tu asistente IA de prueba. 

Estoy aquí para ayudarte con:
- 📊 Cotizaciones personalizadas
- 💡 Información de productos  
- 🤝 Consultas comerciales
- 📋 Soporte técnico

¿En qué puedo asistirte hoy?"""
        
        else:
            replies = [
                "Entiendo tu consulta. Puedo ayudarte con información detallada sobre nuestros productos y servicios.",
                "Excelente pregunta. Permíteme revisar nuestro catálogo para darte la mejor respuesta.",
                "Gracias por contactarnos. Estoy analizando tu solicitud para brindarte una respuesta precisa.",
                f"Perfecto, {client_id}. He procesado tu mensaje y puedo ofrecerte varias opciones."
            ]
            reply = random.choice(replies)
        
        return jsonify({
            'reply': reply,
            'client_name': f'Cliente {client_id}',
            'timestamp': time.time()
        })
        
    except Exception as e:
        return jsonify({
            'reply': 'Disculpa, hubo un error procesando tu mensaje. Por favor intenta de nuevo.',
            'error': str(e)
        }), 500

@app.route('/download-test.pdf')
def download_test():
    """Simula descarga de PDF"""
    return """
    <html>
        <body>
            <h1>🎉 ¡Descarga de Prueba Exitosa!</h1>
            <p>Este sería tu PDF de cotización.</p>
            <p>En producción, aquí se descargaría el archivo real.</p>
        </body>
    </html>
    """

@app.route('/')
def status():
    return jsonify({
        'status': 'Servidor de prueba activo',
        'endpoints': {
            'chat': '/chat-api',
            'download': '/download-test.pdf'
        }
    })

if __name__ == '__main__':
    print("🚀 Iniciando servidor de prueba en puerto 5001...")
    print("🔗 Widget URL: http://localhost:5001/chat-api")
    print("📋 Status: http://localhost:5001/")
    app.run(debug=False, port=5001, host='127.0.0.1')