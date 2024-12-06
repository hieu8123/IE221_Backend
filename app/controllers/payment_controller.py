from flask import Blueprint, request, jsonify, redirect
from app.middlewares.auth import token_required, admin_required
from app.services.vnpay_service import VNPayService
from app.services.order_service import OrderService
from app.services.refund_service import RefundService
from app.services.auth_serivce import AuthService
from app.services.product_service import ProductService
from app.services.cart_service import CartService
from app.services.address_service import AddressService
from app.configs.vnpay_configs import VNPAYConfig

payment_blueprint = Blueprint("payment", __name__)

@payment_blueprint.route('/vnpay/create_payment', methods=['POST'])
@token_required
def create_payment():
    """
    API tạo giao dịch thanh toán với VNPAY.
    """
    data = request.json
    order_id = data.get("order_id")
    cart_items = data.get("cartItems", [])
    name = data.get("name")
    phone = data.get("phone")
    email = data.get("email")
    order_info = data.get("order_info")
    address = data.get("address")
    client_ip = request.remote_addr
   

    user_id = AuthService.decode_jwt_from_cookie()[0]['id']

    if not all([cart_items]):
        return jsonify({"error": "Missing required parameters"}), 400
    
    # Tính tổng số tiền cần thanh toán
    total_amount = sum(
        (cart_item.get('product') or {}).get("price", 0) * cart_item.get("quantity", 1)
        for cart_item in cart_items
    )

    if address.get("id"):
        address_id = address.get("id")
        address = AddressService.get_address_by_id(address_id)
        if not address:
            return jsonify({'error': 'Address not found'}), 404
    else:
        address_id = AddressService.create_address(user_id, 
                                                    address.get("address_line"), 
                                                    address.get("city"), 
                                                    address.get("country"),
                                                    address.get("postal_code"),
                                                    address.get("note")).id

    if order_id:
        order = OrderService.get_order_by_id(order_id)
    else:
        order = OrderService.create_order(user_id = user_id, 
                                          status="pending payment",
                                          note="Thanh toan don hang Hieu Store" ,
                                          name= name,
                                          phone=phone,
                                          email=email,
                                          address_id=address_id,
                                          total=total_amount )
        CartService.clear_user_cart(user_id)
        for product in [cart_item.get('product') for cart_item in cart_items]:
            OrderService.create_order_detail(order.id, product.get("id"), product.get("price"), product.get("quantity"))
            ProductService.update_product_quantity_and_buyturn(product.get("id"), product.get("quantity"))
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
        order_id = int(vnpay_params.get('vnp_TxnRef'))

        # Kiểm tra chữ ký
        is_valid_signature = VNPayService.verify_signature(vnpay_params, secure_hash)
        if not is_valid_signature:
            OrderService.update_order_status(order_id, 'error')
            return jsonify({'success': False, 'message': 'Invalid signature'}), 400
        
        response_code = vnpay_params.get('vnp_ResponseCode')
        transaction_id = vnpay_params.get('vnp_TransactionNo')
        order = OrderService.get_order_by_id(order_id)
        user_id = order.user_id
        CartService.clear_user_cart(user_id)


        # Kiểm tra mã phản hồi từ VNPAY (00 là thanh toán thành công)
        if response_code == '00':
            OrderService.update_order_status(order_id, 'paid')
            OrderService.update_transaction_id(transaction_id, order_id)
            return redirect(f"{VNPAYConfig.FRONTEND_URL}/check-out/success?order_id={order_id}&status=SUCCESS")
        
        OrderService.update_order_status(order_id, 'error')
        return redirect(f"{VNPAYConfig.FRONTEND_URL}/check-out/fail?order_id={order_id}&status=FAILED&response_code={response_code}")
    except Exception as e:
        print(e)
        return redirect(f"{VNPAYConfig.FRONTEND_URL}/check-out/fail?order_id={order_id}&status=FAILED&response_code=99")
    
@payment_blueprint.route('/vnpay/request_refund', methods=['POST'])
@token_required
def request_refund():
    data = request.get_json()

    order_id = int(data.get('order_id'))
    reason = data.get('reason', 'No reason provided')

    # Kiểm tra đơn hàng có tồn tại không
    order = OrderService.get_order_by_id(order_id)

    if not order:
        return jsonify({'message': 'Order not found'}), 404
    
    
    user_id = int(AuthService.decode_jwt_from_cookie()[0]['id'])

    if order.user_id != user_id:
        return jsonify({'message': 'You are not allowed to refund this order'}), 403
    
    # Kiểm tra trạng thái đơn hàng (chỉ hoàn tiền nếu đơn hàng chưa được hoàn tiền)
    if order.status == 'refunded':
        return jsonify({'message': 'This order has already been refunded'}), 400

    # Tạo yêu cầu hoàn tiền
    RefundService.create_refund_request(order.id, order.total, reason)

    return jsonify({'message': 'Refund request created successfully'}), 201


@payment_blueprint.route('/vnpay/refund/<int:refund_id>', methods=['POST'])
@admin_required
def approve_refund(refund_id):
    # Lấy yêu cầu hoàn tiền theo ID
    refund_request = RefundService.get_refund_request_by_id(refund_id)
    if not refund_request:
        return jsonify({'message': 'Refund request not found'}), 404
    
    # Kiểm tra trạng thái yêu cầu (chỉ có thể phê duyệt yêu cầu đang chờ)
    if refund_request.status != 'pending':
        return jsonify({'message': 'This refund request is already processed'}), 400
    
    # Thực hiện hoàn tiền qua VNPAY
    refund_result = VNPayService.create_refund(refund_request.order, refund_request.order.total, refund_request.reason)
    
    if refund_result is None:
        return jsonify({'message': 'Refund failed, please try again later(the result is None)'}), 500

    if refund_result.get('vnp_ResponseCode') == '00':
        # Nếu hoàn tiền thành công
        refund_request.status = 'approved'
        OrderService.update_order_status(refund_request.order_id, 'refunded')
        RefundService.update_refund_request_status(refund_id, 'approved')
        return jsonify({'message': 'Refund request approved and order refunded'}), 200
    else:
        # Nếu hoàn tiền thất bại
        return jsonify({'message': 'Refund failed, please try again later'}), 500

