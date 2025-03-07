from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import User, Course, student_course

student_bp = Blueprint('student_bp', __name__)

@student_bp.route('/my-grades', methods=['GET'])
@jwt_required()
def get_student_grades():
    current_user_id = get_jwt_identity()
    current_user = User.query.filter_by(username=current_user_id).first()
    if current_user.role != "student":
        return jsonify({"error": "Unauthorized: Student access required"}), 403
    grades = current_user.grades
    grade_data = [{
        'id': g.id, 'course_id': g.course_id, 'grade': g.grade, 
        'course': {'name': g.course.name} if g.course else None
    } for g in grades]
    return jsonify(grade_data), 200

@student_bp.route('/enroll', methods=['POST'])
@jwt_required()
def enroll_in_course():
    current_user_id = get_jwt_identity()
    current_user = User.query.filter_by(username=current_user_id).first()
    if current_user.role != "student":
        return jsonify({"error": "Unauthorized: Student access required"}), 403
    data = request.get_json()
    course_id = data.get('course_id')
    course = Course.query.get_or_404(course_id)
    # Check if already enrolled
    if db.session.query(student_course).filter_by(student_id=current_user.id, course_id=course_id).first():
        return jsonify({"error": "Already enrolled in this course"}), 400
    # Enroll
    db.session.execute(student_course.insert().values(student_id=current_user.id, course_id=course_id))
    db.session.commit()
    return jsonify({"message": "Enrolled successfully"}), 200

@student_bp.route('/my-courses', methods=['GET'])
@jwt_required()
def get_my_courses():
    current_user_id = get_jwt_identity()
    current_user = User.query.filter_by(username=current_user_id).first()
    if current_user.role != "student":
        return jsonify({"error": "Unauthorized: Student access required"}), 403
    courses = Course.query.join(student_course).filter(student_course.c.student_id == current_user.id).all()
    course_data = [{'id': c.id, 'name': c.name, 'instructor_id': c.instructor_id} for c in courses]
    return jsonify(course_data), 200
