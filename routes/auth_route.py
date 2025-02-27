from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User
from bcrypt import hashpw, gensalt, checkpw  # Use Bcrypt for hashing and verification

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not all(key in data for key in ['username', 'password']):
        return jsonify({"error": "Missing username or password"}), 400

    user = User.query.filter_by(username=data['username']).first()
    if user and checkpw(data['password'].encode('utf-8'), user.password):
        access_token = create_access_token(identity=user.id)
        return jsonify({"token": access_token, "user": {"id": user.id, "username": user.username, "role": 'admin' if user.is_admin else 'instructor' if user.is_instructor else 'student'}}), 200
    return jsonify({"error": "Invalid credentials"}), 401

@auth_bp.route('/signup', methods=['POST'])
def signup():
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
    # Set role flags based on input (default to student, pending for instructor)
    new_user.is_admin = data.get('is_admin', False)
    new_user.is_instructor = data.get('is_instructor', False)  # Default to False (pending) for instructors
    new_user.is_student = data.get('is_student', True)  # Default to student

    try:
        db.session.add(new_user)
        db.session.commit()
        # For instructors, return a message indicating pending approval (per your specs)
        if new_user.is_instructor:
            return jsonify({"message": "Please wait for admin verification"}), 201
        access_token = create_access_token(identity=new_user.id)
        return jsonify({"token": access_token, "user": {"id": new_user.id, "username": new_user.username, "role": 'student'}}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to signup: {str(e)}"}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    # Note: JWT doesn't have a built-in logout like sessions, but you can invalidate tokens or clear client-side tokens
    return jsonify({"message": "Logged out successfully (client must clear token)"}), 200