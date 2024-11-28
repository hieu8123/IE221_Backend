from datetime import datetime
import hashlib
import hmac
import urllib.parse
import requests
from app.configs.vnpay_configs import VNPAYConfig
import unicodedata
import json
import random
from flask import request

class VNPayService:
    @staticmethod
    def __hmacsha512(key, data):
        byteKey = key.encode('utf-8')
        byteData = data.encode('utf-8')
        return hmac.new(byteKey, byteData, hashlib.sha512).hexdigest()

    @staticmethod
    def create_payment_url(order_id, amount, order_info, client_ip):
        """
        Tạo URL thanh toán của VNPAY.
        - order_id: ID đơn hàng.
        - amount: Số tiền (VND, đơn vị nhỏ nhất).
        - order_info: Thông tin đơn hàng.
        - client_ip: Địa chỉ IP của client.
        """
                # Chuỗi cần chuyển
        date_str = "20241122173015"

        # Chuyển chuỗi thành đối tượng datetime
        date_obj = datetime.strptime(date_str, "%Y%m%d%H%M%S")

        # Sử dụng strftime để chuyển đối tượng datetime thành chuỗi có định dạng mong muốn
        formatted_date = date_obj.strftime("%Y%m%d%H%M%S")

        params = {
            "vnp_Version": "2.1.0",
            "vnp_Command": "pay",
            "vnp_TmnCode": VNPAYConfig.VNP_TMNCODE,
            "vnp_Amount": int(amount) * 100,  # Nhân 100 vì đơn vị của VNPAY là đồng nhỏ nhất
            "vnp_CurrCode": "VND",
            "vnp_TxnRef": order_id,
            "vnp_OrderInfo": order_info,
            "vnp_OrderType": "billpayment",
            "vnp_ReturnUrl": VNPAYConfig.VNP_RETURN_URL,
            "vnp_IpAddr": client_ip,
            "vnp_Locale": "vn",
            "vnp_CreateDate": formatted_date,
        }

        # Sắp xếp và tạo chữ ký
        sorted_params = sorted(params.items())
        query_string = ''
        seq = 0
        for key, val in sorted_params:
                    if seq == 1:
                        query_string = query_string + "&" + key + '=' + urllib.parse.quote_plus(str(val))
                    else:
                        seq = 1
                        query_string = key + '=' + urllib.parse.quote_plus(str(val))

        signature = VNPayService.__hmacsha512(VNPAYConfig.VNP_HASHSECRET, query_string)
        # Tạo URL thanh toán
        payment_url = f"{VNPAYConfig.VNP_URL}?{query_string}&vnp_SecureHash={signature}"

        print("payment_url:", payment_url)
        return payment_url
    
    @staticmethod
    def verify_signature(vnpay_params, secure_hash):
        """
        Kiểm tra chữ ký (secure_hash) từ VNPAY để xác thực tính toàn vẹn của dữ liệu.
        :param vnpay_params: Các tham số từ callback của VNPAY.
        :param secure_hash: Chữ ký được gửi từ VNPAY.
        :return: True nếu chữ ký hợp lệ, False nếu không hợp lệ.
        """
        # Loại bỏ secure_hash khỏi tham số trước khi tạo lại chữ ký
        vnpay_params_dict = vnpay_params.to_dict()
        vnpay_params_dict.pop('vnp_SecureHash') if 'vnp_SecureHash' in vnpay_params else None
        inputData = sorted(vnpay_params_dict.items())
        query_string = ''
        seq = 0
        for key, val in inputData:
            if str(key).startswith('vnp_'):
                if seq == 1:
                    query_string = query_string + "&" + key + '=' + urllib.parse.quote_plus(str(val))
                else:
                    seq = 1
                    query_string = key + '=' + urllib.parse.quote_plus(str(val))

        # Tính chữ ký mới từ query_string
        new_secure_hash = VNPayService.__hmacsha512(VNPAYConfig.VNP_HASHSECRET, query_string)

        # Kiểm tra chữ ký có khớp không
        return new_secure_hash == secure_hash

    @staticmethod
    def create_refund(order, refund_amount, reason):
        """Gửi yêu cầu hoàn tiền qua VNPAY."""
        n = random.randint(10**11, 10**12 - 1)
        n_str = str(n)
        while len(n_str) < 12:
            n_str = '0' + n_str
        url = VNPAYConfig.VNP_API_URL
        secret_key = VNPAYConfig.VNP_HASHSECRET
        vnp_TmnCode = VNPAYConfig.VNP_TMNCODE
        vnp_RequestId = n_str
        vnp_Version = '2.1.0'
        vnp_Command = 'refund'
        vnp_TransactionType = '03'
        vnp_TxnRef = order.id
        vnp_Amount = int(order.total)  # Đổi sang đơn vị VNĐ
        vnp_OrderInfo = order.note
        vnp_TransactionNo = order.transaction_id
        vnp_TransactionDate = order.created_at.strftime('%Y%m%d%H%M%S')
        vnp_CreateDate = datetime.now().strftime('%Y%m%d%H%M%S')
        vnp_CreateBy = 'admin'
        vnp_IpAddr = request.remote_addr

        print(vnp_Amount)

        hash_data = "|".join([
        str(vnp_RequestId), str(vnp_Version), str(vnp_Command), str(vnp_TmnCode), 
        str(vnp_TransactionType), str(vnp_TxnRef), str(vnp_Amount), str(vnp_TransactionNo), 
        str(vnp_TransactionDate), str(vnp_CreateBy), str(vnp_CreateDate), 
        str(vnp_IpAddr), str(vnp_OrderInfo)
        ])


        secure_hash = hmac.new(secret_key.encode(), hash_data.encode(), hashlib.sha512).hexdigest()

        reason =  unicodedata.normalize('NFKD', reason)
        reason = ''.join([c for c in reason if not unicodedata.combining(c)])

        data = {
        "vnp_RequestId": vnp_RequestId,
        "vnp_TmnCode": vnp_TmnCode,
        "vnp_Command": vnp_Command,
        "vnp_TxnRef": vnp_TxnRef,
        "vnp_Amount": vnp_Amount,
        "vnp_OrderInfo": vnp_OrderInfo,
        "vnp_TransactionDate": vnp_TransactionDate,
        "vnp_CreateDate": vnp_CreateDate,
        "vnp_IpAddr": vnp_IpAddr,
        "vnp_TransactionType": vnp_TransactionType,
        "vnp_TransactionNo": vnp_TransactionNo,
        "vnp_CreateBy": vnp_CreateBy,
        "vnp_Version": vnp_Version,
        "vnp_SecureHash": secure_hash
        }
        # Sắp xếp và tạo chữ ký
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))

            print(response.text)

            if response.status_code == 200:
                response_json = json.loads(response.text)
            else:
                response_json = {"error": f"Request failed with status code: {response.status_code}"}

            return response_json
        except Exception as e:
            print(e)
            return {"error": str(e)}