from flask import Flask, request, jsonify
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
from flask_cors import CORS
from config import Config
from production import ProductionConfig
from sqlalchemy import text
import os

# Load environment variables
load_dotenv()  
# Initialize Flask app
app = Flask(__name__)

# Load configuration based on environment
if os.getenv('FLASK_ENV') == 'production':
    app.config.from_object(ProductionConfig)
else:
    app.config.from_object(Config)

# Initialize CORS
CORS(app, resources=Config.CORS_RESOURCES)

# Initialize extensions
db = SQLAlchemy(app)
ma = Marshmallow(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Import models and schemas
from models import User, Student, Instructor, Course, Grade, student_course
from schemas import StudentSchema, CourseSchema, InstructorSchema, GradeSchema, UserSchema

# Import blueprints
from routes.admin_routes import admin_bp
from routes.auth_route import auth_bp
from routes.student_route import student_bp
from routes.instructor_route import instructor_bp
# Register Blueprints
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(student_bp, url_prefix='/api/students')
app.register_blueprint(instructor_bp, url_prefix='/api/instructors')

# Protected route example
@app.route('/api/protected', methods=['GET'])
@jwt_required()
def protected():
    try:
        current_user = get_jwt_identity()
        return jsonify({'message': f'Hello, {current_user}! You are authenticated.'}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to access protected route: {str(e)}"}), 500

# Existing API endpoints for your models
@app.route('/api/students', methods=['GET'])
@jwt_required()
def get_students():
    try:
        students = Student.query.all()
        return StudentSchema(many=True).dump(students), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch students: {str(e)}"}), 500

@app.route('/api/instructors', methods=['GET'])
@jwt_required()
def get_instructors():
    try:
        instructors = Instructor.query.all()
        return InstructorSchema(many=True).dump(instructors), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch instructors: {str(e)}"}), 500

@app.route('/api/courses', methods=['GET'])
@jwt_required()
def get_courses():
    try:
        courses = Course.query.all()
        return CourseSchema(many=True).dump(courses), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch courses: {str(e)}"}), 500

@app.route('/api/students/<int:student_id>/courses/<int:course_id>', methods=['POST'])
@jwt_required()
def enroll_student_in_course(student_id, course_id):
    try:
        student = Student.query.get_or_404(student_id)
        course = Course.query.get_or_404(course_id)
        student.courses.append(course)
        db.session.commit()
        return jsonify({'message': 'Student enrolled successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to enroll student: {str(e)}"}), 500

# Check database connection
with app.app_context():
    try:
        db.session.execute(text('SELECT 1'))
        print("Database connection successful!")
    except Exception as e:
        print(f"Database connection failed: {e}")

if __name__ == '__main__':
    app.run(debug=True)