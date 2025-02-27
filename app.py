from flask import Flask
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db  
from config import Config  
from sqlalchemy.sql import text
from schemas import ma
from routes import admin_bp, auth_bp 
from flask_jwt_extended import JWTManager

# Initialize Flask app
app = Flask(__name__)

# Load configuration
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
ma.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)  # Initialize JWTManager for JWT authentication

# Register Blueprints
app.register_blueprint(admin_bp)
app.register_blueprint(auth_bp)

with app.app_context():
    try:
        db.session.execute(text('SELECT 1'))
        print("Database connection successful!")
    except Exception as e:
        print(f"Database connection failed: {e}")

if __name__ == '__main__':
    app.run()