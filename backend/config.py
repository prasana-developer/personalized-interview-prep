import os
from dotenv import load_dotenv

# Load environment variables from .env file located at project root
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

load_dotenv(os.path.join(BASE_DIR, '..', '.env'))

class Config:
    BASE_DIR = BASE_DIR
    # Secret key for JWT signing
    SECRET_KEY = os.getenv('SECRET_KEY', 'super-secret-key-123')
    # Gemini API key
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    # SQLite database location
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'app.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Upload settings
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB limit
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
