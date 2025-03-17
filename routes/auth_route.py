from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from extensions import db, bcrypt  
from models import User, Student  

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    from extensions import db, bcrypt  
    from models import User
    data = request.get_json()
    if not data or not all(key in data for key in ['username', 'password']):
        return jsonify({'message': 'Username and password are required'}), 400
    user = User.query.filter_by(username=data['username']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity=user.username)
        return jsonify({
            "token": access_token,
            "user": {
                "id": user.id,
                "username": user.username,
                "role": 'admin' if user.is_admin else 'instructor' if user.is_instructor else 'student'
            }
        }), 200
    return jsonify({'message': 'Invalid credentials'}), 401

@auth_bp.route('/signup', methods=['POST'])
def signup():
    from extensions import db, bcrypt  
    from models import User, Student  
    data = request.get_json()
    if not data or not all(key in data for key in ['username', 'email', 'password']):
        return jsonify({'message': 'Missing required fields: username, email, and password'}), 400
    existing_user = User.query.filter_by(username=data['username']).first()
    if existing_user:
        return jsonify({'message': 'Username already exists'}), 400
    existing_email = User.query.filter_by(email=data['email']).first()
    if existing_email:
        return jsonify({'message': 'Email already exists'}), 400
    first_user = User.query.first() is None
    is_admin = data.get('is_admin', False)
    is_instructor = data.get('is_instructor', False)
    is_student = data.get('is_student', False)
    if not (is_admin or is_instructor or is_student):
        is_student = True
    if first_user and not is_admin:
        return jsonify({'message': 'The first user (id=1) must be an admin'}), 400
    hashed_password = bcrypt.generate_password_hash(data['password'])
    new_user = User(
        username=data['username'],
        email=data['email'],
        password=hashed_password,
        is_admin=is_admin,
        is_instructor=is_instructor,
        is_student=is_student
    )
    try:
        db.session.add(new_user)
        db.session.commit()
        new_user.validate_roles()
        if new_user.is_student:
            new_student = Student(
                id=new_user.id,
                username=new_user.username,
                email=new_user.email,
                password=new_user.password,
                is_student=True
            )
            db.session.add(new_student)
            db.session.commit()
            access_token = create_access_token(identity=new_user.username)
            return jsonify({
                "token": access_token,
                "user": {
                    "id": new_user.id,
                    "username": new_user.username,
                    "role": "student"
                }
            }), 201
        elif new_user.is_instructor:
            return jsonify({'message': 'Instructor signup pending admin verification'}), 201
        else:  
            access_token = create_access_token(identity=new_user.username)
            return jsonify({
                "token": access_token,
                "user": {
                    "id": new_user.id,
                    "username": new_user.username,
                    "role": "admin" if new_user.is_admin else "instructor"
                }
            }), 201
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to signup: {str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    return jsonify({'message': 'Logged out successfully (client must clear token)'}), 200