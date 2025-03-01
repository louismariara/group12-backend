from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Course, Student, Grade, Instructor
from schemas import CourseSchema, StudentSchema, GradeSchema

# Initialize the Blueprint
instructor_bp = Blueprint('instructor', __name__, url_prefix='/api/instructor')

# Initialize schemas
course_schema = CourseSchema()
courses_schema = CourseSchema(many=True)
student_schema = StudentSchema()
students_schema = StudentSchema(many=True)
grade_schema = GradeSchema()
grades_schema = GradeSchema(many=True)

# Route to view all courses
@instructor_bp.route('/courses', methods=['GET'])
@jwt_required()
def get_all_courses():
    try:
        courses = Course.query.all()
        return jsonify(courses_schema.dump(courses)), 200
    except Exception as e:
        return jsonify({'error': f'Failed to fetch courses: {str(e)}'}), 500

# Route to view courses taught by the instructor
@instructor_bp.route('/my-courses', methods=['GET'])
@jwt_required()
def get_my_courses():
    try:
        instructor_username = get_jwt_identity()
        instructor = Instructor.query.filter_by(username=instructor_username).first()
        if not instructor:
            return jsonify({'message': 'Instructor not found'}), 404

        courses = Course.query.filter_by(instructor_id=instructor.id).all()
        return jsonify(courses_schema.dump(courses)), 200
    except Exception as e:
        return jsonify({'error': f'Failed to fetch your courses: {str(e)}'}), 500

# Route to edit a course
@instructor_bp.route('/courses/<int:course_id>', methods=['PUT'])
@jwt_required()
def update_course(course_id):
    try:
        instructor_username = get_jwt_identity()
        instructor = Instructor.query.filter_by(username=instructor_username).first()
        if not instructor:
            return jsonify({'message': 'Instructor not found'}), 404

        course = Course.query.filter_by(id=course_id, instructor_id=instructor.id).first()
        if not course:
            return jsonify({'message': 'Course not found or you are not the instructor'}), 404

        data = request.get_json()
        if 'name' in data:
            course.name = data['name']
        if 'duration' in data:
            course.duration = data['duration']

        db.session.commit()
        return jsonify(course_schema.dump(course)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update course: {str(e)}'}), 500

# Route to view students enrolled in a course
@instructor_bp.route('/courses/<int:course_id>/students', methods=['GET'])
@jwt_required()
def get_students_in_course(course_id):
    try:
        instructor_username = get_jwt_identity()
        instructor = Instructor.query.filter_by(username=instructor_username).first()
        if not instructor:
            return jsonify({'message': 'Instructor not found'}), 404

        course = Course.query.filter_by(id=course_id, instructor_id=instructor.id).first()
        if not course:
            return jsonify({'message': 'Course not found or you are not the instructor'}), 404

        students = course.students
        return jsonify(students_schema.dump(students)), 200
    except Exception as e:
        return jsonify({'error': f'Failed to fetch students: {str(e)}'}), 500

# Route to view grades in a course
@instructor_bp.route('/courses/<int:course_id>/grades', methods=['GET'])
@jwt_required()
def get_grades_in_course(course_id):
    try:
        instructor_username = get_jwt_identity()
        instructor = Instructor.query.filter_by(username=instructor_username).first()
        if not instructor:
            return jsonify({'message': 'Instructor not found'}), 404

        course = Course.query.filter_by(id=course_id, instructor_id=instructor.id).first()
        if not course:
            return jsonify({'message': 'Course not found or you are not the instructor'}), 404

        grades = Grade.query.filter_by(course_id=course_id).all()
        return jsonify(grades_schema.dump(grades)), 200
    except Exception as e:
        return jsonify({'error': f'Failed to fetch grades: {str(e)}'}), 500

# Route to edit a grade
@instructor_bp.route('/grades/<int:grade_id>', methods=['PUT'])
@jwt_required()
def update_grade(grade_id):
    try:
        instructor_username = get_jwt_identity()
        instructor = Instructor.query.filter_by(username=instructor_username).first()
        if not instructor:
            return jsonify({'message': 'Instructor not found'}), 404

        grade = Grade.query.filter_by(id=grade_id).first()
        if not grade:
            return jsonify({'message': 'Grade not found'}), 404

        course = Course.query.filter_by(id=grade.course_id, instructor_id=instructor.id).first()
        if not course:
            return jsonify({'message': 'You are not the instructor for this course'}), 403

        data = request.get_json()
        if 'grade' in data:
            grade.grade = data['grade']
        if 'comments' in data:
            grade.comments = data['comments']

        db.session.commit()
        return jsonify(grade_schema.dump(grade)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update grade: {str(e)}'}), 500