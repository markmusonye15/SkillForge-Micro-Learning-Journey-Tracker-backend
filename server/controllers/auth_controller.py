from flask import request, jsonify, Blueprint
from flask_jwt_extended import create_access_token
from ..models import db
from ..models.user import User


auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/register', methods=['POST'])
def register_user():
    """Handles new user registration via the API."""
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"msg": "Username and password are required"}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({"msg": "Username already exists"}), 409

    # The User model's password setter will automatically hash this
    user = User(username=data['username'], password=data['password'])
    db.session.add(user)
    db.session.commit()

    return jsonify({"msg": "User created successfully"}), 201

@auth_bp.route('/login', methods=['POST'])
def login_user():
    """Handles user login and returns a JWT access token."""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    # The 'verify_password' method is in your User model
    if user and user.verify_password(password):
        # Create a new token with the user's id as the identity
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200

    return jsonify({"msg": "Bad username or password"}), 401

