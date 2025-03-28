from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db, bcrypt
from supabase import create_client, Client
import os
from models import User, Grade, Course, Instructor

admin_bp = Blueprint('admin', __name__)
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_ANON_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

@admin_bp.route('/users', methods=['POST'])
@jwt_required()
def create_user():
    from schemas import UserSchema
    user_schema = UserSchema()
    current_user_id = get_jwt_identity()
    current_user = User.query.filter_by(username=current_user_id).first()
    if not current_user.is_admin:
        return jsonify({"error": "Unauthorized: Admin access required"}), 403
    data = request.get_json()
    if not data or not all(key in data for key in ['username', 'email', 'password']):
        return jsonify({"error": "Missing required fields: username, email, and password"}), 400
    existing_user = User.query.filter_by(username=data['username']).first()
    if existing_user:
        return jsonify({"error": "Username already exists"}), 400
    existing_email = User.query.filter_by(email=data['email']).first()
    if existing_email:
        return jsonify({"error": "Email already exists"}), 400
    new_user = User(
        username=data['username'],
        email=data['email'],
        password=bcrypt.generate_password_hash(data['password'].encode('utf-8'))
    )
    new_user.is_admin = data.get('is_admin', False)
    new_user.is_instructor = data.get('is_instructor', False)
    new_user.is_student = data.get('is_student', True)
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify(user_schema.dump(new_user)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to create user: {str(e)}"}), 500

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.filter_by(username=current_user_id).first()
        if not current_user or not current_user.is_admin:
            return jsonify({"error": "Unauthorized: Admin access required"}), 403
        all_users = User.query.all()
        user_data = [{
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': 'instructor' if user.is_instructor else 'student' if user.is_student else 'admin',
            'is_instructor_verified': Instructor.query.filter_by(id=user.id).first().is_instructor_verified if user.is_instructor and Instructor.query.filter_by(id=user.id).first() else False
        } for user in all_users]
        return jsonify(user_data), 200
    except Exception as e:
        print(f"Error in get_users: {str(e)}")
        return jsonify({"error": f"Failed to fetch users: {str(e)}"}), 500

@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.filter_by(username=current_user_id).first()
    if not current_user.is_admin:
        return jsonify({"error": "Unauthorized: Admin access required"}), 403
    target_user = User.query.get_or_404(user_id)
    user_data = {
        'id': target_user.id,
        'username': target_user.username,
        'email': target_user.email,
        'role': 'instructor' if target_user.is_instructor else 'student'
    }
    return jsonify(user_data), 200

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.filter_by(username=current_user_id).first()
    if not current_user.is_admin:
        return jsonify({"error": "Unauthorized: Admin access required"}), 403
    target_user = User.query.get_or_404(user_id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    if 'username' in data:
        existing_user = User.query.filter_by(username=data['username']).first()
        if existing_user and existing_user.id != user_id:
            return jsonify({"error": "Username already exists"}), 400
        target_user.username = data['username']
    if 'email' in data:
        existing_email = User.query.filter_by(email=data['email']).first()
        if existing_email and existing_email.id != user_id:
            return jsonify({"error": "Email already exists"}), 400
        target_user.email = data['email']
    if 'password' in data:
        target_user.password = bcrypt.generate_password_hash(data['password'].encode('utf-8'))
    is_instructor = data.get('is_instructor', None)
    if is_instructor is not None:
        target_user.is_instructor = bool(is_instructor)
        if target_user.is_instructor:
            target_user.is_student = False
    is_student = data.get('is_student', None)
    if is_student is not None:
        target_user.is_student = bool(is_student)
        if target_user.is_student:
            target_user.is_instructor = False
    target_user.is_admin = data.get('is_admin', target_user.is_admin)
    try:
        db.session.commit()
        user_data = {
            'id': target_user.id,
            'username': target_user.username,
            'email': target_user.email,
            'role': 'instructor' if target_user.is_instructor else 'student'
        }
        return jsonify(user_data), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update user: {str(e)}"}), 500

@admin_bp.route('/users/<int:user_id>/approve-instructor', methods=['PUT'])
@jwt_required()
def approve_instructor(user_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.filter_by(username=current_user_id).first()
    if not current_user or not current_user.is_admin:
        return jsonify({"error": "Unauthorized: Admin access required"}), 403
    target_user = User.query.get_or_404(user_id)
    if not target_user.is_instructor:
        return jsonify({"error": "User is not requested as an instructor"}), 400
    instructor = Instructor.query.filter_by(id=target_user.id).first()
    if not instructor:
        instructor = Instructor(
            id=target_user.id,
            username=target_user.username,
            email=target_user.email,
            password=target_user.password,
            is_instructor=True,
            is_instructor_verified=True
        )
        db.session.add(instructor)
    else:
        instructor.is_instructor_verified = True
    try:
        db.session.commit()
        return jsonify({"message": f"Instructor {target_user.username} approved"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to approve instructor: {str(e)}"}), 500

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.filter_by(username=current_user_id).first()
    if not current_user.is_admin:
        return jsonify({"error": "Unauthorized: Admin access required"}), 403
    target_user = User.query.get_or_404(user_id)
    try:
        db.session.delete(target_user)
        db.session.commit()
        return jsonify({"message": "User deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete user: {str(e)}"}), 500

@admin_bp.route('/courses', methods=['POST'])
@jwt_required()
def create_course():
    from extensions import db
    from models import Course, User
    from schemas import CourseSchema
    course_schema = CourseSchema()
    current_user_id = get_jwt_identity()
    current_user = User.query.filter_by(username=current_user_id).first()
    if not current_user.is_admin:
        return jsonify({"error": "Unauthorized: Admin access required"}), 403

   
    if 'image_file' in request.files:
        file = request.files['image_file']
        file_name = file.filename
        try:
            file_content = file.read()
            response = supabase.storage.from_("course_images").upload(file_name, file_content)
            image_url = f"https://group12-backend-cv2o.supabase.co/storage/v1/object/public/course_images/{file_name}"
            return jsonify({"image": image_url}), 200
        except Exception as e:
            return jsonify({"error": f"Failed to upload image: {str(e)}"}), 500

    
    data = request.get_json()
    if not data or not all(key in data for key in ['name', 'duration']):
        return jsonify({"error": "Missing required fields: name and duration"}), 400
    new_course = Course(
        name=data["name"],
        duration=data["duration"],
        image=data.get("image", None),
        modules=data.get("modules", None),
    )
    try:
        db.session.add(new_course)
        db.session.commit()
        return jsonify(course_schema.dump(new_course)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to create course: {str(e)}"}), 500

@admin_bp.route('/courses', methods=['GET'])
@jwt_required()
def get_courses():
    try:
        from schemas import CourseSchema
        courses_schema = CourseSchema(many=True)
        current_user_id = get_jwt_identity()
        current_user = User.query.filter_by(username=current_user_id).first()
        if not current_user or not current_user.is_admin:
            return jsonify({"error": "Unauthorized: Admin access required"}), 403
        courses = Course.query.all()
        return jsonify(courses_schema.dump(courses)), 200
    except Exception as e:
        print(f"Error in get_courses: {str(e)}")
        return jsonify({"error": f"Failed to fetch courses: {str(e)}"}), 500

@admin_bp.route('/courses/<int:course_id>', methods=['GET'])
@jwt_required()
def get_course(course_id):
    from schemas import CourseSchema
    course_schema = CourseSchema()
    current_user_id = get_jwt_identity()
    current_user = User.query.filter_by(username=current_user_id).first()
    if not current_user.is_admin:
        return jsonify({"error": "Unauthorized: Admin access required"}), 403
    course = Course.query.get_or_404(course_id)
    return jsonify(course_schema.dump(course)), 200

@admin_bp.route('/courses/<int:course_id>', methods=['PUT'])
@jwt_required()
def update_course(course_id):
    from schemas import CourseSchema
    import logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    course_schema = CourseSchema()
    current_user_id = get_jwt_identity()
    current_user = User.query.filter_by(username=current_user_id).first()
    if not current_user.is_admin:
        logger.warning(f"Unauthorized access attempt by {current_user_id}")
        return jsonify({"error": "Unauthorized: Admin access required"}), 403
    
    course = Course.query.get_or_404(course_id)
    data = request.get_json()
    logger.debug(f"Received data for course {course_id}: {data}")
    
    if not data:
        logger.error("No data provided in request")
        return jsonify({"error": "No data provided"}), 400
    
    if 'name' in data:
        course.name = data['name']
    if 'duration' in data:
        course.duration = data['duration']
    if 'image' in data:
        course.image = data['image']
        logger.debug(f"Updated image for course {course_id} to {data['image']}")
    if 'instructor_id' in data:  
        course.instructor_id = data['instructor_id']
    
    try:
        db.session.commit()
        logger.info(f"Successfully updated course {course_id}")
        return jsonify(course_schema.dump(course)), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to update course {course_id}: {str(e)}")
        return jsonify({"error": f"Failed to update course: {str(e)}"}), 500

@admin_bp.route('/courses/<int:course_id>', methods=['DELETE'])
@jwt_required()
def delete_course(course_id):
    from schemas import CourseSchema
    current_user_id = get_jwt_identity()
    current_user = User.query.filter_by(username=current_user_id).first()
    if not current_user.is_admin:
        return jsonify({"error": "Unauthorized: Admin access required"}), 403
    course = Course.query.get_or_404(course_id)
    try:
        db.session.delete(course)
        db.session.commit()
        return jsonify({"message": "Course deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete course: {str(e)}"}), 500

@admin_bp.route('/instructors', methods=['GET'])
@jwt_required()
def get_instructors():
    current_user_id = get_jwt_identity()
    current_user = User.query.filter_by(username=current_user_id).first()
    if not current_user or not current_user.is_admin:
        return jsonify({"error": "Unauthorized: Admin access required"}), 403
    instructors = User.query.filter_by(is_instructor=True).all()
    return jsonify([{"id": i.id, "username": i.username} for i in instructors]), 200

@admin_bp.route('/grades', methods=['GET'])
@jwt_required()
def get_grades():
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.filter_by(username=current_user_id).first()
        if not current_user or not current_user.is_admin:
            return jsonify({"error": "Unauthorized: Admin access required"}), 403
        grades = Grade.query.all()
        grade_data = [{
            'id': g.id,
            'student_id': g.student_id,
            'course_id': g.course_id,
            'grade': g.grade,
            'course': {'name': g.course.name} if g.course else None
        } for g in grades]
        return jsonify(grade_data), 200
    except Exception as e:
        print(f"Error in get_grades: {str(e)}")
        return jsonify({"error": f"Failed to fetch grades: {str(e)}"}), 500

@admin_bp.route('/grades', methods=['POST'])
@jwt_required()
def create_grade():
    current_user_id = get_jwt_identity()
    current_user = User.query.filter_by(username=current_user_id).first()
    if not current_user.is_admin:
        return jsonify({"error": "Unauthorized: Admin access required"}), 403
    data = request.get_json()
    student_id = data.get('student_id')
    course_id = data.get('course_id')
    grade_value = data.get('grade')
    if not all([student_id, course_id, grade_value]):
        return jsonify({"error": "Missing required fields"}), 400
    new_grade = Grade(student_id=student_id, course_id=course_id, grade=grade_value)
    db.session.add(new_grade)
    db.session.commit()
    return jsonify({"message": "Grade created", "id": new_grade.id}), 201

@admin_bp.route('/grades/<int:grade_id>', methods=['PUT'])
@jwt_required()
def update_grade(grade_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.filter_by(username=current_user_id).first()
    if not current_user.is_admin:
        return jsonify({"error": "Unauthorized: Admin access required"}), 403
    grade = Grade.query.get_or_404(grade_id)
    data = request.get_json()
    grade.student_id = data.get('student_id', grade.student_id)
    grade.course_id = data.get('course_id', grade.course_id)
    grade.grade = data.get('grade', grade.grade)
    db.session.commit()
    return jsonify({"message": "Grade updated"}), 200

@admin_bp.route('/grades/<int:grade_id>', methods=['DELETE'])
@jwt_required()
def delete_grade(grade_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.filter_by(username=current_user_id).first()
    if not current_user.is_admin:
        return jsonify({"error": "Unauthorized: Admin access required"}), 403
    grade = Grade.query.get_or_404(grade_id)
    db.session.delete(grade)
    db.session.commit()
    return jsonify({"message": "Grade deleted"}), 200