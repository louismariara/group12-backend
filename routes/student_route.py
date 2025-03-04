from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from schemas import CourseSchema, GradeSchema
from extensions import db

# Initialize the Blueprint
student_bp = Blueprint('student', __name__)

# Initialize schemas
course_schema = CourseSchema()
courses_schema = CourseSchema(many=True)
grade_schema = GradeSchema()
grades_schema = GradeSchema(many=True)

# Route to view all courses (read-only)
@student_bp.route('/my-grades', methods=['GET'])
@jwt_required()
def get_my_grades():
    from extensions import db
    from models import User, Student, Grade 
    from schemas import GradeSchema
    grades_schema = GradeSchema(many=True)
    try:
        student_username = get_jwt_identity()
        user = User.query.filter_by(username=student_username).first()
        if not user or not user.is_student:
            return jsonify({'message': 'Student not found or not a student'}), 404
        if user.is_admin:
            return jsonify({'message': 'Admins cannot view student grades here'}), 403
        student = Student.query.filter_by(username=student_username).first()
        if not student:
            return jsonify({'message': 'Student not found'}), 404
        grades = Grade.query.filter_by(student_id=student.id).all()
        return jsonify(grades_schema.dump(grades)), 200
    except Exception as e:
        return jsonify({'error': f'Failed to fetch your grades: {str(e)}'}), 500

@student_bp.route('/courses', methods=['GET'])
@jwt_required()
def get_all_courses():
    from extensions import db
    from models import Course
    from schemas import CourseSchema
    courses_schema = CourseSchema(many=True)
    try:
        courses = Course.query.all()
        return jsonify(courses_schema.dump(courses)), 200
    except Exception as e:
        return jsonify({'error': f'Failed to fetch courses: {str(e)}'}), 500