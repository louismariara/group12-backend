from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity  # Replace flask_login import with this
from models import db, User, Course, Grade
from schemas import ma, UserSchema, CourseSchema, GradeSchema  # Import all schemas from schemas
from bcrypt import hashpw, gensalt  # Replace werkzeug.security with bcrypt

# Create a Blueprint for admin routes
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

user_schema = UserSchema()
users_schema = UserSchema(many=True)
course_schema = CourseSchema()
courses_schema = CourseSchema(many=True)
grade_schema = GradeSchema()
grades_schema = GradeSchema(many=True)

# CRUD Operations for Users (Admin Only)

# Create a new user (POST /admin/users)
@admin_bp.route('/users', methods=['POST'])
@jwt_required()  # Replace @login_required
def create_user():
    user_id = get_jwt_identity()  # Get user ID from JWT token
    user = User.query.get_or_404(user_id)
    if not user.is_admin:
        return jsonify({"error": "Unauthorized: Admin access required"}), 403

    data = request.get_json()
    if not data or not all(key in data for key in ['username', 'email', 'password']):
        return jsonify({"error": "Missing required fields: username, email, and password"}), 400

    # Check if username or email already exists
    existing_user = User.query.filter_by(username=data['username']).first()
    if existing_user:
        return jsonify({"error": "Username already exists"}), 400

    existing_email = User.query.filter_by(email=data['email']).first()
    if existing_email:
        return jsonify({"error": "Email already exists"}), 400

    # Create new user with hashed password (using Bcrypt)
    new_user = User(
        username=data['username'],
        email=data['email'],
        password=hashpw(data['password'].encode('utf-8'), gensalt())
    )
    # Set role flags based on input (default to student if not specified, pending for instructor)
    new_user.is_admin = data.get('is_admin', False)
    new_user.is_instructor = data.get('is_instructor', False)  # Admin can set this directly or leave pending
    new_user.is_student = data.get('is_student', True)  # Default to student if no roles specified

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify(user_schema.dump(new_user)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to create user: {str(e)}"}), 500

# Read all users (GET /admin/users)
@admin_bp.route('/users', methods=['GET'])
@jwt_required()  # Replace @login_required
def get_users():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    if not user.is_admin:
        return jsonify({"error": "Unauthorized: Admin access required"}), 403

    users = User.query.all()
    # Format user data for the table: include id, username, email, and role (instructor/student)
    user_data = [{
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': 'instructor' if user.is_instructor else 'student'
    } for user in users]
    return jsonify(user_data), 200

# Read a specific user by ID (GET /admin/users/<id>)
@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()  # Replace @login_required
def get_user(user_id):
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    if not user.is_admin:
        return jsonify({"error": "Unauthorized: Admin access required"}), 403

    user = User.query.get_or_404(user_id)
    # Format user data for the table: include id, username, email, and role (instructor/student)
    user_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': 'instructor' if user.is_instructor else 'student'
    }
    return jsonify(user_data), 200

# Update a user (PUT /admin/users/<id>)
@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()  # Replace @login_required
def update_user(user_id):
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    if not user.is_admin:
        return jsonify({"error": "Unauthorized: Admin access required"}), 403

    user = User.query.get_or_404(user_id)
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Update username if provided and not already taken
    if 'username' in data:
        existing_user = User.query.filter_by(username=data['username']).first()
        if existing_user and existing_user.id != user_id:
            return jsonify({"error": "Username already exists"}), 400
        user.username = data['username']

    # Update email if provided and not already taken
    if 'email' in data:
        existing_email = User.query.filter_by(email=data['email']).first()
        if existing_email and existing_email.id != user_id:
            return jsonify({"error": "Email already exists"}), 400
        user.email = data['email']

    # Update password if provided (hash it with Bcrypt)
    if 'password' in data:
        user.password = hashpw(data['password'].encode('utf-8'), gensalt())

    # Update role flags, with special handling for instructor approval
    if 'is_instructor' in data:
        # If setting is_instructor to True, this acts as admin approval
        user.is_instructor = bool(data['is_instructor'])
        # If is_instructor is set to True, ensure is_student is False (instructor can't be both)
        if user.is_instructor:
            user.is_student = False
    if 'is_student' in data:
        user.is_student = bool(data['is_student'])
        # If is_student is set to True, ensure is_instructor is False (student can't be instructor)
        if user.is_student:
            user.is_instructor = False
    user.is_admin = data.get('is_admin', user.is_admin)  # Admin can only update this for others

    try:
        db.session.commit()
        # Return formatted data for the table
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': 'instructor' if user.is_instructor else 'student'
        }
        return jsonify(user_data), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update user: {str(e)}"}), 500

# Delete a user (DELETE /admin/users/<id>)
@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()  # Replace @login_required
def delete_user(user_id):
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    if not user.is_admin:
        return jsonify({"error": "Unauthorized: Admin access required"}), 403

    user = User.query.get_or_404(user_id)
    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete user: {str(e)}"}), 500

# CRUD Operations for Courses (Admin Only)

# Create a new course (POST /admin/courses)
@admin_bp.route('/courses', methods=['POST'])
@jwt_required()  # Replace @login_required
def create_course():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    if not user.is_admin:
        return jsonify({"error": "Unauthorized: Admin access required"}), 403

    data = request.get_json()
    if not data or not all(key in data for key in ['name', 'duration']):
        return jsonify({"error": "Missing required fields: name and duration"}), 400

    new_course = Course(
        name=data['name'],
        duration=data['duration'],
        description=data.get('description', None)
    )

    try:
        db.session.add(new_course)
        db.session.commit()
        return jsonify(course_schema.dump(new_course)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to create course: {str(e)}"}), 500

# Read all courses (GET /admin/courses)
@admin_bp.route('/courses', methods=['GET'])
@jwt_required()  # Replace @login_required
def get_courses():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    if not user.is_admin:
        return jsonify({"error": "Unauthorized: Admin access required"}), 403

    courses = Course.query.all()
    return jsonify(courses_schema.dump(courses)), 200

# Read a specific course by ID (GET /admin/courses/<id>)
@admin_bp.route('/courses/<int:course_id>', methods=['GET'])
@jwt_required()  # Replace @login_required
def get_course(course_id):
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    if not user.is_admin:
        return jsonify({"error": "Unauthorized: Admin access required"}), 403

    course = Course.query.get_or_404(course_id)
    return jsonify(course_schema.dump(course)), 200

# Update a course (PUT /admin/courses/<id>)
@admin_bp.route('/courses/<int:course_id>', methods=['PUT'])
@jwt_required()  # Replace @login_required
def update_course(course_id):
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    if not user.is_admin:
        return jsonify({"error": "Unauthorized: Admin access required"}), 403

    course = Course.query.get_or_404(course_id)
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    if 'name' in data:
        course.name = data['name']
    if 'duration' in data:
        course.duration = data['duration']
    if 'description' in data:
        course.description = data['description']

    try:
        db.session.commit()
        return jsonify(course_schema.dump(course)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update course: {str(e)}"}), 500

# Delete a course (DELETE /admin/courses/<id>)
@admin_bp.route('/courses/<int:course_id>', methods=['DELETE'])
@jwt_required()  # Replace @login_required
def delete_course(course_id):
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    if not user.is_admin:
        return jsonify({"error": "Unauthorized: Admin access required"}), 403

    course = Course.query.get_or_404(course_id)
    try:
        db.session.delete(course)
        db.session.commit()
        return jsonify({"message": "Course deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete course: {str(e)}"}), 500

# CRUD Operations for Grades (Admin Only)

# Create a new grade (POST /admin/grades)
@admin_bp.route('/grades', methods=['POST'])
@jwt_required()  # Replace @login_required
def create_grade():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    if not user.is_admin:
        return jsonify({"error": "Unauthorized: Admin access required"}), 403

    data = request.get_json()
    if not data or not all(key in data for key in ['student_id', 'course_id', 'grade']):
        return jsonify({"error": "Missing required fields: student_id, course_id, and grade"}), 400

    new_grade = Grade(
        student_id=data['student_id'],
        course_id=data['course_id'],
        grade=data['grade']
    )

    try:
        db.session.add(new_grade)
        db.session.commit()
        return jsonify(grade_schema.dump(new_grade)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to create grade: {str(e)}"}), 500

# Read all grades (GET /admin/grades)
@admin_bp.route('/grades', methods=['GET'])
@jwt_required()  # Replace @login_required
def get_grades():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    if not user.is_admin:
        return jsonify({"error": "Unauthorized: Admin access required"}), 403

    grades = Grade.query.all()
    return jsonify(grades_schema.dump(grades)), 200

# Read a specific grade by ID (GET /admin/grades/<id>)
@admin_bp.route('/grades/<int:grade_id>', methods=['GET'])
@jwt_required()  # Replace @login_required
def get_grade(grade_id):
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    if not user.is_admin:
        return jsonify({"error": "Unauthorized: Admin access required"}), 403

    grade = Grade.query.get_or_404(grade_id)
    return jsonify(grade_schema.dump(grade)), 200

# Update a grade (PUT /admin/grades/<id>)
@admin_bp.route('/grades/<int:grade_id>', methods=['PUT'])
@jwt_required()  # Replace @login_required
def update_grade(grade_id):
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    if not user.is_admin:
        return jsonify({"error": "Unauthorized: Admin access required"}), 403

    grade = Grade.query.get_or_404(grade_id)
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    if 'grade' in data:
        grade.grade = data['grade']

    try:
        db.session.commit()
        return jsonify(grade_schema.dump(grade)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update grade: {str(e)}"}), 500

# Delete a grade (DELETE /admin/grades/<id>)
@admin_bp.route('/grades/<int:grade_id>', methods=['DELETE'])
@jwt_required()  # Replace @login_required
def delete_grade(grade_id):
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    if not user.is_admin:
        return jsonify({"error": "Unauthorized: Admin access required"}), 403

    grade = Grade.query.get_or_404(grade_id)
    try:
        db.session.delete(grade)
        db.session.commit()
        return jsonify({"message": "Grade deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete grade: {str(e)}"}), 500