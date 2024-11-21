from functools import wraps
from datetime import datetime
from app.services.auth_serivce import AuthService
from flask import jsonify, g
from app.services.user_service import UserService

# Hàm kiểm tra người dùng đã đăng nhập chưa
def token_required(func):
    """Wrapper để kiểm tra JWT trong cookie của request."""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        # Kiểm tra JWT trong cookie
        decoded, error = AuthService.decode_jwt_from_cookie()

        
        if error:
            return jsonify({'message': error}), 401  # Trả về lỗi nếu không có token hoặc token không hợp lệ
        
        user_id = decoded.get('id')
        user = UserService.get_user_by_id(user_id)

        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        g.token = decoded
        return func(*args, **kwargs)  # Tiếp tục thực hiện hàm được bao bọc

    return decorated_function

# Hàm kiểm tra vai trò là admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Kiểm tra token và lấy thông tin người dùng
        decoded, error = AuthService.decode_jwt_from_cookie()

        if error:
            return jsonify({'message': error}), 401  # Trả về lỗi nếu không có token hoặc token không hợp lệ
        
        user_id = decoded.get('id')
        user = UserService.get_user_by_id(user_id)

        # Kiểm tra xem người dùng có vai trò yêu cầu không
        if user.role != "ROLE_ADMIN":
            return jsonify({'message': f'You do not have the required permissions'}), 403  # 403 Forbidden

        g.token = decoded
        return f(*args, **kwargs)  # Tiếp tục thực hiện hàm gốc

    return decorated_function
    

