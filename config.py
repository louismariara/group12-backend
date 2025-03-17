from dotenv import load_dotenv
import os
import logging


logging.basicConfig(level=logging.INFO)

load_dotenv()


logging.info(f"DB_USER: {os.getenv('DB_USER')}")
logging.info(f"DB_PASSWORD: {os.getenv('DB_PASSWORD')}")
logging.info(f"DB_HOST: {os.getenv('DB_HOST')}")
logging.info(f"DB_PORT: {os.getenv('DB_PORT')}")
logging.info(f"DB_NAME: {os.getenv('DB_NAME')}")
logging.info(f"SECRET_KEY: {os.getenv('SECRET_KEY')}")
logging.info(f"JWT_SECRET_KEY: {os.getenv('JWT_SECRET_KEY')}")


required_vars = ['DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT', 'DB_NAME', 'SECRET_KEY', 'JWT_SECRET_KEY']
missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Missing environment variables: {', '.join(missing_vars)}")


class Config:
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    CORS_RESOURCES = {r"/api/*": {"origins": CORS_ORIGINS}}
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = 3600 
    DEBUG = False