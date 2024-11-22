import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///default.db')  # Default DB nếu không có biến môi trường
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')  # Mặc định là 'default-secret-key'
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024
