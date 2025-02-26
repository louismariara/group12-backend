from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta

# Initialize Flask app
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'super-secret-key-123'  # Use a secure, random key in production
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=15)  # Token expires in 15 minutes

# Initialize extensions
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Mock database (replace with a real database like SQLAlchemy in production)
users = {}

# Registration endpoint
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Basic input validation
    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400
    if len(password) < 6:
        return jsonify({'message': 'Password must be at least 6 characters'}), 400
    if username in users:
        return jsonify({'message': 'User already exists'}), 400

    # Hash the password with bcrypt
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    users[username] = hashed_password
    return jsonify({'message': 'User registered successfully'}), 201

# Login endpoint
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Check credentials
    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400
    if username not in users:
        return jsonify({'message': 'Invalid credentials'}), 401
    if not bcrypt.check_password_hash(users[username], password):
        return jsonify({'message': 'Invalid credentials'}), 401

    # Create JWT token with expiration
    access_token = create_access_token(identity=username)
    return jsonify({'access_token': access_token}), 200

# Protected route
@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify({'message': f'Hello, {current_user}! You are authenticated.'}), 200

# Run the app
if __name__ == '__main__':
    app.run(debug=True)