from flask import Blueprint, request, jsonify
from ..utils.auth_helpers import hash_password, verify_password, generate_jwt
from ..models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'User already exists'}), 400
    user = User(email=email, password_hash=hash_password(password))
    db.session.add(user)
    db.session.commit()
    token = generate_jwt(user.id)
    resp = jsonify({'message': 'User registered'})
    resp.set_cookie('access_token', token, httponly=True, samesite='Lax')
    return resp, 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()
    if not user or not verify_password(password, user.password_hash):
        return jsonify({'error': 'Invalid credentials'}), 401
    token = generate_jwt(user.id)
    resp = jsonify({'message': 'Logged in'})
    resp.set_cookie('access_token', token, httponly=True, samesite='Lax')
    return resp
