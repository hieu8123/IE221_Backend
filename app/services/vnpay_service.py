from datetime import datetime
import hashlib
import hmac
import urllib.parse
from flask import redirect
import requests
from app.configs.vnpay_configs import VNPAYConfig
import unicodedata
import json


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
    def     create_refund(transaction_id, order_id, refund_amount, reason):
        """Gửi yêu cầu hoàn tiền qua VNPAY."""
        vnp_command = "refund"
        vnp_version = "2.1.0"
        vnp_curr_code = "VND"
        vnp_tmn_code = VNPAYConfig.VNP_TMNCODE  # Mã merchant
        vnp_hash_secret = VNPAYConfig.VNP_HASHSECRET  # Secret Key
        vnp_api_url = VNPAYConfig.VNP_URL  # API Refund URL

        reason =  unicodedata.normalize('NFKD', reason)
        reason = ''.join([c for c in reason if not unicodedata.combining(c)])

        # Tạo dữ liệu refund
        vnp_params = {
            "vnp_Command": vnp_command,
            "vnp_Version": vnp_version,
            "vnp_TmnCode": vnp_tmn_code,
            "vnp_TxnRef": order_id,  # Mã đơn hàng
            "vnp_TransactionType": 'refund',  # Loại giao dịch: Refund
            "vnp_TransactionNo": transaction_id,  # Mã giao dịch của VNPAY
            "vnp_Amount": int(refund_amount) * 100,  # Số tiền hoàn (nhân 100)
            "vnp_OrderInfo": reason,
            "vnp_RequestId": datetime.now().strftime("%Y%m%d%H%M%S"),
            "vnp_IpAddr": "127.0.0.1",  # IP của server thực hiện refund
            "vnp_CreateDate": datetime.now().strftime("%Y%m%d%H%M%S"),
        }

        # Sắp xếp và tạo chữ ký
        sorted_params = sorted(vnp_params.items())
        query_string = ''
        seq = 0
        for key, val in sorted_params:
                    if seq == 1:
                        query_string = query_string + "&" + key + '=' + urllib.parse.quote_plus(str(val))
                    else:
                        seq = 1
                        query_string = key + '=' + urllib.parse.quote_plus(str(val))

        signature = VNPayService.__hmacsha512(VNPAYConfig.VNP_HASHSECRET, query_string)
        vnp_params['vnp_SecureHash'] = signature

        # Gửi request đến API của VNPAY
        try:
            response = requests.post(vnp_api_url, json=vnp_params)
            response.raise_for_status()  # Kiểm tra lỗi HTTP
            response_json = response.json()  # Phân tích dữ liệu trả về
        except requests.exceptions.RequestException as e:
            response_json = {"error": f"Request failed: {str(e)}"}

        return response_json