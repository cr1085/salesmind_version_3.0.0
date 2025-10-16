# config.py
import os
from dotenv import load_dotenv
from sqlalchemy.engine import URL
from urllib.parse import quote_plus



load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # --- Construcción Segura de la URL de la Base de Datos ---
    db_user = os.environ.get('DB_USER')
    # db_password = os.environ.get('DB_PASSWORD')
    db_password = quote_plus(os.environ.get('DB_PASSWORD'))
    db_host = os.environ.get('DB_HOST')
    db_port = os.environ.get('DB_PORT')
    db_name = os.environ.get('DB_NAME')

    SQLALCHEMY_DATABASE_URI = URL.create(
        drivername="postgresql+psycopg2",
        username=db_user,
        password=db_password,
        host=db_host,
        port=db_port,
        database=db_name,
    )
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Claves API
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
    AI_PROVIDER = os.environ.get('AI_PROVIDER', 'google')