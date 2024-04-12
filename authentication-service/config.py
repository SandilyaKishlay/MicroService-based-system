import os

# Define the base directory of the project
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    POSTGRES_HOST = os.environ.get('POSTGRES_HOST', 'localhost')
    POSTGRES_PORT = os.environ.get('POSTGRES_PORT', '5432')
    POSTGRES_USER = os.environ.get('POSTGRES_USER', 'your-username')
    POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'your-password')
    POSTGRES_DB = os.environ.get('POSTGRES_DB', 'your-database-name')
    SQLALCHEMY_DATABASE_URI = f'postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

  
