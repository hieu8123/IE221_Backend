from flask import Blueprint, jsonify, request, make_response
from werkzeug.security import generate_password_hash
from app.services.auth_serivce import AuthService
from app.services.user_service import UserService

# Tạo Blueprint cho module auth
auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/login', methods=['POST'])
def login():
    """Xử lý đăng nhập người dùng"""
    email = request.json.get('email')
    password = request.json.get('password')

    if not email or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    # Kiểm tra thông tin đăng nhập
    token, error = AuthService.login(email, password)
    if error:
        return jsonify({'message': error}), 401
    
    # Tạo response
    response = make_response(jsonify({'message': 'Login successful'}), 200)
    AuthService.add_jwt_to_cookie(response, token)

    return response

@auth_blueprint.route('/logout', methods=['POST'])
def logout():
    """Xử lý đăng xuất người dùng"""
    response = make_response(jsonify({'message': 'Logout successful'}), 200)
    AuthService.logout(response)

    return response

@auth_blueprint.route('/register', methods=['POST'])
def register():
    """Xử lý đăng ký người dùng"""
    email = request.json.get('email')
    password = request.json.get('password')
    name = request.json.get('name')
    role = "ROLE_USER"
    avatar = request.json.get('avatar')
    phone = request.json.get('phone')

    if not email or not password or not name:
        return jsonify({'message': 'Email, password and name are required'}), 400

    hashed_password = generate_password_hash(password)
    
    new_user = UserService.create_user(email, hashed_password, name, role, avatar, phone)
    if not new_user:
        return jsonify({'message': 'Register failed'}), 500
    
    token = AuthService.create_jwt(new_user.id, new_user.name, new_user.role)

    response = make_response(jsonify({'message': 'Register successful'}), 201)
    AuthService.add_jwt_to_cookie(response, token)

    return response
