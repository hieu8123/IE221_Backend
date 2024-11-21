from flask import Blueprint, request, jsonify
from app.middlewares.auth import token_required
from app.services.vnpay_service import VNPayService
from app.services.order_service import OrderService
from app.models.refund_request import RefundRequest

payment_blueprint = Blueprint("payment", __name__)

@payment_blueprint.route('/vnpay/create_payment', methods=['POST'])
@token_required
def create_payment():
    """
    API tạo giao dịch thanh toán với VNPAY.
    """
    data = request.json
    order_id = data.get("order_id")
    user_id = data.get("user_id")
    products = data.get("products", [])
    order_info = data.get("order_info")
    client_ip = request.remote_addr

    if not all([user_id, products, order_info]):
        return jsonify({"error": "Missing required parameters"}), 400
    
    # Tính tổng số tiền cần thanh toán
    total_amount = sum(product.get("price", 0) * product.get("quantity", 1) for product in products)

    if order_id:
        order = OrderService.get_order_by_id(order_id)
    else:
        order = OrderService.create_order(user_id = user_id, status="PENDING",note="Thanh toan don hang Hieu Store" ,total=total_amount )
        for product in products:
            OrderService.create_order_detail(order.id, product.get("product_id"), product.get("price"), product.get("quantity"))
    
    # Tạo URL thanh toán
    try:
        payment_url = VNPayService.create_payment_url(order.id,order.total, order.note, client_ip)
        return jsonify({"payment_url": payment_url}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@payment_blueprint.route('/vnpay/callback', methods=['GET'])
def vnpay_callback():
    try:
        vnpay_params = request.args
        secure_hash = vnpay_params.get('vnp_SecureHash')

        # Kiểm tra chữ ký
        is_valid_signature = VNPayService.verify_signature(vnpay_params, secure_hash)
        if not is_valid_signature:
            OrderService.update_order_status(order_id, 'ERROR')
            return jsonify({'success': False, 'message': 'Invalid signature'}), 400

        order_id = vnpay_params.get('vnp_TxnRef')
        response_code = vnpay_params.get('vnp_ResponseCode')

        # Kiểm tra mã phản hồi từ VNPAY (00 là thanh toán thành công)
        if response_code == '00':
            OrderService.update_order_status(order_id, 'PAID')
            return jsonify({'status': 'SUCCESS', 'message': 'Transaction successful'})
        
        OrderService.update_order_status(order_id, 'ERROR')
        return jsonify({'status': 'FAILED', 'message': 'Transaction failed'})
    except Exception as e:
        return jsonify({'status': 'FAILED', 'message': str(e)}), 500
    
@payment_blueprint.route('/vnpay/equest_refund', methods=['POST'])
@token_required
def request_refund():
    data = request.get_json()

    order_id = data.get('order_id')
    amount = data.get('amount')
    reason = data.get('reason')


    # Kiểm tra đơn hàng có tồn tại không
    order = OrderService.get_order_by_id(order_id)
    if not order:
        return jsonify({'message': 'Order not found'}), 404
    
    # Kiểm tra trạng thái đơn hàng (chỉ hoàn tiền nếu đơn hàng chưa được hoàn tiền)
    if order.status == 'refunded':
        return jsonify({'message': 'This order has already been refunded'}), 400

    # Tạo yêu cầu hoàn tiền
    refund_request = RefundRequest(
        order_id=order_id,
        amount=amount,
        reason=reason
    )


    return jsonify({'message': 'Refund request created successfully'}), 201