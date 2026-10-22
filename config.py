import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'rewear-ai-fashion-super-secret-key-2026')
    
    # MySQL Database Configuration
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = os.getenv('MYSQL_PORT', '3306')
    MYSQL_DB = os.getenv('MYSQL_DB', 'preowned_fashion_db')
    
    # Database Configuration:
    # Set USE_MYSQL=True and your MYSQL_PASSWORD in .env to connect to your local MySQL instance.
    USE_MYSQL = os.getenv('USE_MYSQL', 'false').lower() in ('true', '1', 'yes')
    
    if USE_MYSQL:
        if MYSQL_PASSWORD:
            SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
        else:
            SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    else:
        SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///preowned_fashion.db')
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload folder
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'avif'}

    # ML Model Path
    MODEL_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'ml_models', 'fair_resale_model.joblib')
