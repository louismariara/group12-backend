from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Course, Student, Grade
from schemas import CourseSchema, GradeSchema

# Initialize the Blueprint
student_bp = Blueprint('student', __name__, url_prefix='/api/student')

# Initialize schemas
course_schema = CourseSchema()
courses_schema = CourseSchema(many=True)
grade_schema = GradeSchema()
grades_schema = GradeSchema(many=True)

# Route to view all courses (read-only)
@student_bp.route('/courses', methods=['GET'])
@jwt_required()
def get_all_courses():
    try:
        # Fetch all courses from the database
        courses = Course.query.all()
        return jsonify(courses_schema.dump(courses)), 200
    except Exception as e:
        return jsonify({'error': f'Failed to fetch courses: {str(e)}'}), 500

# Route to view the student's grades
@student_bp.route('/my-grades', methods=['GET'])
@jwt_required()
def get_my_grades():
    try:
        # Get the logged-in student's username from the JWT token
        student_username = get_jwt_identity()
        
        # Fetch the student from the database
        student = Student.query.filter_by(username=student_username).first()
        if not student:
            return jsonify({'message': 'Student not found'}), 404

        # Fetch grades for the logged-in student
        grades = Grade.query.filter_by(student_id=student.id).all()
        return jsonify(grades_schema.dump(grades)), 200
    except Exception as e:
        return jsonify({'error': f'Failed to fetch your grades: {str(e)}'}), 500