import jwt
import datetime
from flask import jsonify, make_response, request, current_app as app
from app.models.user import User
from werkzeug.security import generate_password_hash, check_password_hash


class AuthService:
    @staticmethod
    def create_jwt(user_id, username, role):
        """Tạo JWT token với thông tin người dùng và vai trò"""
        token = jwt.encode({
            'id': user_id,    # ID của người dùng
            'sub': username,  # subject (user)
            'role': role,     # role của người dùng (admin, user, v.v.)
            'iat': datetime.datetime.utcnow(),  # Thời điểm tạo token
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Token hết hạn sau 1 giờ
        }, app.config['SECRET_KEY'], algorithm='HS256')
        return token

    @staticmethod
    def decode_jwt(token):
        """Giải mã JWT và trả về payload"""
        try:
            # Giải mã token
            decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            return decoded  # Trả về thông tin đã giải mã (payload)
        except jwt.ExpiredSignatureError:
            return {'message': 'Token has expired!'}
        except jwt.InvalidTokenError:
            return {'message': 'Invalid token!'}

    @staticmethod
    def add_jwt_to_cookie(response, token):
        """Thêm JWT vào cookie của response"""
        # Thêm token vào cookie

        response.headers.add(
            'Set-Cookie',
            f'ie221_access_token={token}; '
            f'Path=/; '
            f'Max-Age=3600; '
            f'Expires={datetime.datetime.utcnow() + datetime.timedelta(hours=1)}; '
            f'HttpOnly; '
            f'SameSite=None; '
            f'Secure; '
            f'Partitioned'
        )


        # response.set_cookie(
        #     'ie221_access_token',  # Tên cookie
        #     token,           # Giá trị cookie (JWT token)
        #     max_age=datetime.timedelta(hours=1),  # Thời gian sống của cookie (1 giờ)
        #     expires=datetime.datetime.utcnow() + datetime.timedelta(hours=1),  # Thời gian hết hạn của cookie
        #     secure=True,     # Chỉ gửi cookie qua kết nối HTTPS
        #     httponly=True,   # Chỉ có thể truy cập cookie từ server, không thể từ JavaScript
        #     samesite='None' # Cho phép sử dụng cookie trong cross-site
        # )
        
        return response

    @staticmethod
    def decode_jwt_from_cookie():
        """Trích xuất và giải mã JWT từ cookie"""
        token = request.cookies.get('ie221_access_token')  # Lấy JWT từ cookie 'ie221_access_token'
        
        if not token:
            return None, 'No token found in cookies'
        
        try:
            # Giải mã token
            decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            return decoded, None  # Trả về payload đã giải mã, hoặc None nếu không có lỗi
        except jwt.ExpiredSignatureError:
            return None, 'Token has expired'
        except jwt.InvalidTokenError:
            return None, 'Invalid token'
    

    @staticmethod
    def login(email, password):
        """Xác thực thông tin đăng nhập và trả về JWT nếu hợp lệ"""
        user = User.query.filter_by(email=email).first()
        if not user:
            return None, 'User not found'
        
        if not check_password_hash(user.password, password):
            return None, 'Invalid password'
        
        token = AuthService.create_jwt(user.id, user.name, user.role)
        return token, None
    
    @staticmethod
    def logout(response):
        """Xóa cookie chứa JWT để đăng xuất"""
        response.set_cookie('ie221_access_token', '', expires=0)  # Xóa cookie 'ie221_access_token'




