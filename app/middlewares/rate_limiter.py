from flask import request, jsonify
from time import time

# Lưu lượt truy cập từ từng IP
visit_log = {}

# Cấu hình giới hạn
RATE_LIMIT = 5  # Số yêu cầu tối đa
TIME_FRAME = 60  # Thời gian giới hạn (giây)

def limit_requests():
    """Middleware để giới hạn số lượng yêu cầu từ một IP."""
    client_ip = request.remote_addr  # Lấy địa chỉ IP của client
    current_time = time()

    if client_ip not in visit_log:
        visit_log[client_ip] = []

    # Xóa các lượt truy cập đã quá khung thời gian
    visit_log[client_ip] = [
        timestamp for timestamp in visit_log[client_ip]
        if timestamp > current_time - TIME_FRAME
    ]

    # Kiểm tra số lượng yêu cầu còn lại
    if len(visit_log[client_ip]) >= RATE_LIMIT:
        return jsonify({'error': 'Too many requests. Please slow down.'}), 429

    # Ghi nhận yêu cầu mới
    visit_log[client_ip].append(current_time)
