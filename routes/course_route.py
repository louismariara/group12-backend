from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import db, Course
from schemas import ma, CourseSchema


courses_bp = Blueprint('courses', __name__, url_prefix='/courses')

class CourseSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Course
        include_fk = True
        load_instance = True

course_schema = CourseSchema()
courses_schema = CourseSchema(many=True)


@courses_bp.route('/', methods=['POST'])
@login_required
def create_course():
    if not current_user.is_admin:
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


@courses_bp.route('/', methods=['GET'])
@login_required
def get_courses():
    courses = Course.query.all()
    return jsonify(courses_schema.dump(courses)), 200


@courses_bp.route('/<int:course_id>', methods=['GET'])
@login_required
def get_course(course_id):
    course = Course.query.get_or_404(course_id)
    return jsonify(course_schema.dump(course)), 200


@courses_bp.route('/<int:course_id>', methods=['PUT'])
@login_required
def update_course(course_id):
    if not current_user.is_admin:
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


@courses_bp.route('/<int:course_id>', methods=['DELETE'])
@login_required
def delete_course(course_id):
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
