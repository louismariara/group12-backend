from dotenv import load_dotenv
import os
import logging


load_dotenv('/home/louis-mariara/Documents/phase5/project5/.env')


logging.info(f"DB_USER: {os.getenv('DB_USER')}")
logging.info(f"DB_PASSWORD: {os.getenv('DB_PASSWORD')}")
logging.info(f"DB_HOST: {os.getenv('DB_HOST')}")
logging.info(f"DB_PORT: {os.getenv('DB_PORT')}")
logging.info(f"DB_NAME: {os.getenv('DB_NAME')}")
# Validate required environment variables
required_vars = ['DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT', 'DB_NAME']
missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Missing environment variables: {', '.join(missing_vars)}")

# Flask configuration
class Config:
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')  
    DEBUG = True  