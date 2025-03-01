from flask import Flask, request, jsonify
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
<<<<<<< HEAD
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
load_dotenv('/home/louis-mariara/Documents/phase5/project5/.env')
=======
from models import db  
from config import Config  
from sqlalchemy.sql import text
from schemas import ma
from routes import admin_bp, auth_bp 
from flask_jwt_extended import JWTManager
>>>>>>> c5c057fbb3c9c7ecd00378e3b84402c5893f565d

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
<<<<<<< HEAD
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
=======
jwt = JWTManager(app)  # Initialize JWTManager for JWT authentication

# Register Blueprints
app.register_blueprint(admin_bp)
app.register_blueprint(auth_bp)
>>>>>>> c5c057fbb3c9c7ecd00378e3b84402c5893f565d

# Import models and schemas
from models import User, Student, Instructor, Course, Grade, student_course
from schemas import StudentSchema, CourseSchema, InstructorSchema, GradeSchema, UserSchema

# Import blueprints
from routes.admin_routes import admin_bp
from routes.auth_route import auth_bp

# Register Blueprints
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(auth_bp, url_prefix='/api/auth')

# Authentication routes
@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'message': 'Username and password are required'}), 400
        if len(password) < 6:
            return jsonify({'message': 'Password must be at least 6 characters'}), 400
        if User.query.filter_by(username=username).first():
            return jsonify({'message': 'User already exists'}), 400

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(
            username=username,
            password=hashed_password,
            is_student=data.get('is_student', True),
            is_instructor=data.get('is_instructor', False),
            is_admin=data.get('is_admin', False)
        )

        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to register: {str(e)}'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'message': 'Username and password are required'}), 400
        user = User.query.filter_by(username=username).first()
        if not user or not bcrypt.check_password_hash(user.password, password.encode('utf-8')):
            return jsonify({'message': 'Invalid credentials'}), 401

        access_token = create_access_token(identity=username, expires_delta=timedelta(hours=1))
        return jsonify({'access_token': access_token}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to log in: {str(e)}"}), 500

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