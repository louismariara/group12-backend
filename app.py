from flask import Flask, request, jsonify
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_jwt_extended import jwt_required, get_jwt_identity
from dotenv import load_dotenv
from flask_cors import CORS
from config import Config
from production import ProductionConfig
from sqlalchemy import text
import os
import logging
from extensions import db, bcrypt, jwt
from routes.admin_routes import admin_bp
from routes.auth_route import auth_bp
from routes.student_route import student_bp
from routes.instructor_route import instructor_bp
from models import Course  # Import at top
from schemas import CourseSchema  # Import at top

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Load configuration based on environment
if os.getenv('FLASK_ENV') == 'production':
    app.config.from_object(ProductionConfig)
else:
    app.config.from_object(Config)

# Logging setup (override config.py's basic setup if needed)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Configure CORS using config values
CORS(app, resources=app.config['CORS_RESOURCES'], supports_credentials=True)

# Initialize extensions
db.init_app(app)
ma = Marshmallow(app)
migrate = Migrate(app, db)
bcrypt.init_app(app)
jwt.init_app(app)

# Register blueprints
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(student_bp, url_prefix='/api/students')
app.register_blueprint(instructor_bp, url_prefix='/api/instructors')

# Custom decorator to skip JWT for OPTIONS
def jwt_required_optional(fn):
    def wrapper(*args, **kwargs):
        if request.method == 'OPTIONS':
            logger.debug(f"Handling OPTIONS request for {request.path}")
            return '', 200  # Allow preflight requests without JWT
        return jwt_required()(fn)(*args, **kwargs)
    wrapper.__name__ = fn.__name__  # Preserve endpoint name
    return wrapper

@app.route('/api/courses', methods=['GET', 'OPTIONS'])
@jwt_required_optional
def get_courses():
    if request.method == 'OPTIONS':
        logger.debug("Handling OPTIONS request for /api/courses")
        return '', 200
    try:
        logger.debug("Fetching all courses")
        courses = Course.query.all()
        logger.debug(f"Found {len(courses)} courses")
        result = CourseSchema(many=True).dump(courses)
        logger.debug("Courses serialized successfully")
        return result, 200
    except Exception as e:
        logger.error(f"Error in get_courses: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to fetch courses: {str(e)}"}), 500

@app.route('/api/courses/<int:course_id>', methods=['GET', 'OPTIONS'])
@jwt_required_optional
def get_course(course_id):
    if request.method == 'OPTIONS':
        logger.debug(f"Handling OPTIONS request for /api/courses/{course_id}")
        return '', 200
    try:
        logger.debug(f"Fetching course with ID: {course_id}")
        course = Course.query.get_or_404(course_id)
        logger.debug("Course found, serializing data")
        result = CourseSchema().dump(course)
        return result, 200
    except Exception as e:
        logger.error(f"Error fetching course {course_id}: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to fetch course: {str(e)}"}), 500

# Check database connection and create tables
with app.app_context():
    try:
        db.create_all()  # Ensure tables are created
        db.session.execute(text('SELECT 1'))
        print("Database connection successful and tables created!")
    except Exception as e:
        print(f"Database connection failed: {e}")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Get port from environment, default to 5000
    app.run(debug=True, host='0.0.0.0', port=port)