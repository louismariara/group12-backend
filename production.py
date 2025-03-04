import os
import logging
from config import Config

class ProductionConfig(Config):
    DEBUG = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    SECRET_KEY = os.getenv('SECRET_KEY')
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'https://your-production-frontend.com').split(',')
    CORS_RESOURCES = {r"/api/*": {"origins": CORS_ORIGINS}}
    SQLALCHEMY_ECHO = False  # Explicitly disable query logging
    logging.basicConfig(filename='app.log', level=logging.INFO)  