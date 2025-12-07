
![Banner de 3CB Soluciones y Cristian Cuadrado](https://raw.githubusercontent.com/cr1085/cr1085/refs/heads/main/assets/headerventas.png)


![Banner de 3CB Soluciones y Cristian Cuadrado](https://raw.githubusercontent.com/cr1085/cr1085/refs/heads/main/assets/headermente.png)


SalesMind: Asistente de Ventas con IA para Telegram
SalesMind es un asistente de ventas conversacional impulsado por un modelo de IA generativa (Google Gemini) y una arquitectura RAG (Generación Aumentada por Recuperación). El bot se conecta a Telegram y está diseñado para responder preguntas de clientes basándose en una base de conocimiento personalizada (catálogos de productos, listas de precios, etc., en formato PDF).

El proyecto está construido sobre una base de Python y Flask, y está optimizado para ser desplegado en un entorno de producción como un VPS usando Gunicorn y Nginx.

🚀 Características Principales
Núcleo de IA con RAG: El bot no inventa respuestas. Utiliza una base de datos vectorial (FAISS) creada a partir de tus documentos para encontrar la información más relevante y construir una respuesta precisa.

Personalidad de Ventas: El prompt del sistema está cuidadosamente diseñado para que la IA actúe como "SalesMind", un asistente de ventas amigable, eficiente y servicial.

Sistema de Cotización: Capaz de responder a preguntas sobre precios y características de productos si esta información se encuentra en los PDFs de la base de conocimiento.

Traspaso a Humano (Handoff): Detecta cuándo un usuario necesita hablar con una persona y proporciona instrucciones claras para contactar a un asesor.

Integración con Telegram: Utiliza la API oficial de Telegram a través de webhooks para una comunicación en tiempo real.

Arquitectura Escalable: Desplegado con Gunicorn y Nginx, permitiendo que el bot maneje múltiples conversaciones de manera eficiente y corra como un servicio persistente en segundo plano.

🛠️ Stack Tecnológico
Backend: Python 3, Flask

Servidor de Aplicaciones: Gunicorn

Proxy Inverso: Nginx

IA y Embeddings:

Modelo Generativo: Google Gemini (gemini-1.5-flash-latest)

Modelo de Embeddings: Google (text-embedding-004)

Orquestación de IA (RAG): LangChain

Base de Datos Vectorial: FAISS (Facebook AI Similarity Search)

Gestión de Dependencias: Pip, venv

📂 Estructura del Proyecto
/SalesMind/
|
|-- app.py                  # Punto de entrada principal de la aplicación Flask.
|-- indexer.py              # Script para procesar los PDFs y crear el índice FAISS.
|-- config.py               # Centraliza la configuración (claves API, rutas).
|-- .env                    # Archivo para almacenar las variables de entorno (claves secretas).
|-- requirements.txt        # Lista de dependencias de Python.
|
|-- /modules/                 # Módulos principales de la aplicación.
|   |-- /assistant/
|   |   |-- core.py         # Lógica central del RAG y la comunicación con la API de IA.
|   |
|   |-- /bot/
|       |-- routes.py       # Define el endpoint del webhook para Telegram.
|
|-- /biblioteca_pdfs/         # Carpeta donde debes colocar tus catálogos en PDF.
|
|-- /faiss_index_maestra/     # Carpeta donde se guarda el índice vectorial generado.
|
|-- /venv/                    # Entorno virtual de Python.

⚙️ Guía de Instalación y Despliegue
Sigue estos pasos para poner en marcha el proyecto en un servidor VPS (ej. Contabo).

1. Clonar el Repositorio
Conéctate a tu servidor y clona el proyecto desde GitHub.

git clone git@github.com:tu_usuario/SalesMind.git
cd SalesMind

2. Configurar el Entorno
# Crear un entorno virtual
python3 -m venv venv

# Activar el entorno
source venv/bin/activate

# Instalar las dependencias
pip install -r requirements.txt

3. Configurar Variables de Entorno
Crea un archivo .env en la raíz del proyecto para almacenar tus claves secretas.

nano .env

Añade el siguiente contenido, reemplazando con tus valores reales:

GOOGLE_API_KEY="AIzaSy...tu_clave_de_google"
TELEGRAM_TOKEN="12345:ABC...tu_token_de_telegram"
SECRET_KEY="una_cadena_de_texto_larga_y_secreta_para_flask"

4. Crear la Base de Conocimiento
Sube tus catálogos de productos y servicios en formato PDF a la carpeta /biblioteca_pdfs.

Ejecuta el script indexer.py para procesar los PDFs y crear la base de datos vectorial.

# Asegúrate de que tu entorno virtual esté activado
python indexer.py

Este proceso creará la carpeta faiss_index_maestra.

5. Desplegar con Gunicorn y Nginx
Crear el Servicio systemd: Para que el bot corra como un servicio en segundo plano.

sudo nano /etc/systemd/system/salesmind.service

Pega la siguiente configuración:

[Unit]
Description=Gunicorn instance to serve SalesMind
After=network.target

[Service]
User=tu_usuario
Group=www-data
WorkingDirectory=/home/tu_usuario/SalesMind
ExecStart=/home/tu_usuario/SalesMind/venv/bin/gunicorn -w 4 -b 127.0.0.1:8001 app:app
Restart=always

[Install]
WantedBy=multi-user.target

Configurar Nginx: Para exponer el bot a internet. Edita tu archivo de configuración de Nginx (ej. /etc/nginx/sites-available/default) y añade una nueva location para el bot.

location /salesmind/ {
    rewrite ^/salesmind(/.*)$ $1 break;
    proxy_pass [http://127.0.0.1:8001](http://127.0.0.1:8001);
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}

Activar los Servicios:

# Iniciar y habilitar el servicio del bot
sudo systemctl start salesmind
sudo systemctl enable salesmind

# Probar y reiniciar Nginx
sudo nginx -t
sudo systemctl restart nginx

6. Conectar con Telegram
Finalmente, actualiza el webhook de Telegram para apuntar a tu servidor. Pega la siguiente URL en tu navegador, reemplazando tu IP y tu token:

[https://api.telegram.org/bot](https://api.telegram.org/bot)<TU_TOKEN>/setWebhook?url=http://<TU_IP_PUBLICA>/salesmind/telegram_webhook

¡Tu asistente SalesMind ya está en línea y listo para vender!