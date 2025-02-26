from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import db, Grade
from schemas import ma, GradeSchema


grades_bp = Blueprint('grades', __name__, url_prefix='/grades')


class GradeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Grade
        include_fk = True
        load_instance = True

grade_schema = GradeSchema()
grades_schema = GradeSchema(many=True)


@grades_bp.route('/', methods=['POST'])
@login_required
def create_grade():
    if not current_user.is_admin:
        return jsonify({"error": "Unauthorized: Admin access required"}), 403

    data = request.get_json()
    if not data or not all(key in data for key in ['student_id', 'course_id', 'score']):
        return jsonify({"error": "Missing required fields: student_id, course_id, and score"}), 400

    new_grade = Grade(
        student_id=data['student_id'],
        course_id=data['course_id'],
        score=data['score']
    )

    try:
        db.session.add(new_grade)
        db.session.commit()
        return jsonify(grade_schema.dump(new_grade)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to create grade: {str(e)}"}), 500


@grades_bp.route('/', methods=['GET'])
@login_required
def get_grades():
    if not current_user.is_admin:
        return jsonify({"error": "Unauthorized: Admin access required"}), 403

    grades = Grade.query.all()
    return jsonify(grades_schema.dump(grades)), 200


@grades_bp.route('/<int:grade_id>', methods=['GET'])
@login_required
def get_grade(grade_id):
    if not current_user.is_admin:
        return jsonify({"error": "Unauthorized: Admin access required"}), 403

    grade = Grade.query.get_or_404(grade_id)
    return jsonify(grade_schema.dump(grade)), 200


@grades_bp.route('/<int:grade_id>', methods=['PUT'])
@login_required
def update_grade(grade_id):
    if not current_user.is_admin:
        return jsonify({"error": "Unauthorized: Admin access required"}), 403

    grade = Grade.query.get_or_404(grade_id)
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    if 'score' in data:
        grade.score = data['score']

    try:
        db.session.commit()
        return jsonify(grade_schema.dump(grade)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update grade: {str(e)}"}), 500


@grades_bp.route('/<int:grade_id>', methods=['DELETE'])
@login_required
def delete_grade(grade_id):
    if not current_user.is_admin:
        return jsonify({"error": "Unauthorized: Admin access required"}), 403

    grade = Grade.query.get_or_404(grade_id)
    try:
        db.session.delete(grade)
        db.session.commit()
        return jsonify({"message": "Grade deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete grade: {str(e)}"}), 500
