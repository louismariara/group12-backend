from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Course, User, Student, Grade, Instructor
from schemas import CourseSchema, GradeSchema
from extensions import db

instructor_bp = Blueprint('instructor', __name__)

course_schema = CourseSchema()
courses_schema = CourseSchema(many=True)
grade_schema = GradeSchema()
grades_schema = GradeSchema(many=True)

@instructor_bp.route('/courses', methods=['GET'])
@jwt_required()
def get_all_courses():
    try:
        courses = Course.query.all()
        return jsonify(courses_schema.dump(courses)), 200
    except Exception as e:
        return jsonify({'error': f'Failed to fetch courses: {str(e)}'}), 500
@instructor_bp.route('/my-courses', methods=['GET'])
@jwt_required()
def get_my_courses():
    current_user_id = get_jwt_identity()
    current_user = User.query.filter_by(username=current_user_id).first()
    if not current_user or not current_user.is_instructor:
        return jsonify({"error": "Unauthorized: Instructor access required"}), 403
    courses = Course.query.filter_by(instructor_id=current_user.id).all()
    course_data = [{
        'id': c.id,
        'name': c.name,
        'duration': c.duration,
        'image': c.image,
        'created_at': c.created_at.isoformat() if c.created_at else None,
        'students': [s.id for s in c.students]  
    } for c in courses]
    return jsonify(course_data), 200
@instructor_bp.route('/courses/<int:course_id>', methods=['PUT'])
@jwt_required()
def update_course(course_id):
    try:
        instructor_username = get_jwt_identity()
        instructor = Instructor.query.filter_by(username=instructor_username).first()
        if not instructor or not instructor.is_instructor_verified:
            return jsonify({'message': 'Not a verified instructor'}), 403
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

@instructor_bp.route('/courses/<int:course_id>/students', methods=['GET'])
@jwt_required()
def get_students_in_course(course_id):
    try:
        instructor_username = get_jwt_identity()
        instructor = Instructor.query.filter_by(username=instructor_username).first()
        if not instructor or not instructor.is_instructor_verified:
            return jsonify({'message': 'Not a verified instructor'}), 403
        course = Course.query.filter_by(id=course_id, instructor_id=instructor.id).first()
        if not course:
            return jsonify({'message': 'Course not found or you are not the instructor'}), 404
        students = course.students
        student_data = [{'id': s.id, 'username': s.username} for s in students]
        return jsonify(student_data), 200
    except Exception as e:
        return jsonify({'error': f'Failed to fetch students: {str(e)}'}), 500
    
@instructor_bp.route('/courses', methods=['POST'])
@jwt_required()
def create_instructor_course():
    current_user_id = get_jwt_identity()
    current_user = User.query.filter_by(username=current_user_id).first()
    if not current_user or not current_user.is_instructor:
        return jsonify({"error": "Unauthorized: Instructor access required"}), 403
    data = request.get_json()
    if not all(key in data for key in ['name', 'duration']):
        return jsonify({"error": "Missing required fields: name and duration"}), 400
    new_course = Course(
        name=data['name'],
        duration=data['duration'],
        instructor_id=current_user.id,
        image=data.get('image', None)
    )
    db.session.add(new_course)
    db.session.commit()
    return jsonify({"id": new_course.id, "message": "Course created"}), 201

@instructor_bp.route('/grades', methods=['GET'])
@jwt_required()
def get_instructor_grades():
    instructor_username = get_jwt_identity()
    instructor = Instructor.query.filter_by(username=instructor_username).first()
    if not instructor or not instructor.is_instructor_verified:
        return jsonify({"error": "Unauthorized: Instructor access required"}), 403
    grades = Grade.query.join(Course).filter(Course.instructor_id == instructor.id).all()
    grade_data = [{
        'id': g.id, 'student_id': g.student_id, 'course_id': g.course_id, 
        'grade': g.grade, 'course': {'name': g.course.name}
    } for g in grades]
    return jsonify(grade_data), 200

@instructor_bp.route('/grades', methods=['POST'])
@jwt_required()
def create_instructor_grade():
    instructor_username = get_jwt_identity()
    instructor = Instructor.query.filter_by(username=instructor_username).first()
    if not instructor or not instructor.is_instructor_verified:
        return jsonify({"error": "Unauthorized: Instructor access required"}), 403
    data = request.get_json()
    student_id = data.get('student_id')
    course_id = data.get('course_id')
    grade_value = data.get('grade')
    course = Course.query.get_or_404(course_id)
    if course.instructor_id != instructor.id:
        return jsonify({"error": "Cannot grade a course you don’t teach"}), 403
    new_grade = Grade(student_id=student_id, course_id=course_id, grade=grade_value)
    db.session.add(new_grade)
    db.session.commit()
    return jsonify({"message": "Grade created", "id": new_grade.id}), 201

@instructor_bp.route('/grades/<int:grade_id>', methods=['PUT'])
@jwt_required()
def update_instructor_grade(grade_id):
    instructor_username = get_jwt_identity()
    instructor = Instructor.query.filter_by(username=instructor_username).first()
    if not instructor or not instructor.is_instructor_verified:
        return jsonify({"error": "Unauthorized: Instructor access required"}), 403
    grade = Grade.query.get_or_404(grade_id)
    course = Course.query.get_or_404(grade.course_id)
    if course.instructor_id != instructor.id:
        return jsonify({"error": "Cannot edit grades for a course you don’t teach"}), 403
    data = request.get_json()
    grade.student_id = data.get('student_id', grade.student_id)
    grade.course_id = data.get('course_id', grade.course_id)
    grade.grade = data.get('grade', grade.grade)
    db.session.commit()
    return jsonify({"message": "Grade updated"}), 200

@instructor_bp.route('/grades/<int:grade_id>', methods=['DELETE'])
@jwt_required()
def delete_instructor_grade(grade_id):
    instructor_username = get_jwt_identity()
    instructor = Instructor.query.filter_by(username=instructor_username).first()
    if not instructor or not instructor.is_instructor_verified:
        return jsonify({"error": "Unauthorized: Instructor access required"}), 403
    grade = Grade.query.get_or_404(grade_id)
    course = Course.query.get_or_404(grade.course_id)
    if course.instructor_id != instructor.id:
        return jsonify({"error": "Cannot delete grades for a course you don’t teach"}), 403
    db.session.delete(grade)
    db.session.commit()
    return jsonify({"message": "Grade deleted"}), 200

@instructor_bp.route('/assign-course', methods=['POST'])
@jwt_required()
def assign_course():
    instructor_username = get_jwt_identity()
    instructor = Instructor.query.filter_by(username=instructor_username).first()
    if not instructor or not instructor.is_instructor_verified:
        return jsonify({"error": "Unauthorized: Instructor access required"}), 403
    data = request.get_json()
    course_id = data.get('course_id')
    course = Course.query.get_or_404(course_id)
    if course.instructor_id:
        return jsonify({"error": "Course already assigned to an instructor"}), 400
    course.instructor_id = instructor.id
    db.session.commit()
    return jsonify({"message": "Course assigned successfully"}), 200