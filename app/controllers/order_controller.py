from flask import Blueprint, jsonify, request, make_response
from app.services.order_service import OrderService
from app.services.auth_serivce import AuthService
from app.services.product_service import ProductService
from app.middlewares.auth import token_required, admin_required
from app.services.cart_service import CartService
from app.services.address_service import AddressService

# Tạo Blueprint cho module auth
order_blueprint = Blueprint('order', __name__)

@order_blueprint.route('/get-order', methods=['GET'])
@admin_required
def get_all_orders():
    """ API để lấy danh sách các hóa đơn """
    page = int(request.args.get('page', 1))  # Mặc định là trang 1
    per_page = int(request.args.get('per_page', 10))
    date = request.args.get('date', None)
    order_id = request.args.get('order_id', None)
    pagination_orders = OrderService.get_all_orders_page(order_id=order_id,date=date,page=page, per_page=per_page)
    return jsonify(
        {
        'orders':[{
        'id': order.id,
        'user_id': order.user_id,
        'status': order.status,
        'note': order.note,
        'total': order.total,
        'order_details': [{
                'product_id': order_detail.product_id,
                'price': order_detail.price,
                'quantity': order_detail.quantity,
            } for order_detail in order.details],
        'created_at': order.created_at,
        'updated_at': order.updated_at,
        'transaction_id': order.transaction_id,
    } for order in pagination_orders['orders']],
    'total_pages': pagination_orders['total_pages'],
    'current_page': pagination_orders['current_page']
    }
    ), 200

@order_blueprint.route('/<int:order_id>', methods=['GET'])
def get_order_detail(order_id):
    """ API để lấy thông tin chi tiết của một hóa đơn """
    order = OrderService.get_order_by_id(order_id)

    user_client = AuthService.decode_jwt_from_cookie()[0]
    if order.user_id != user_client['id'] and user_client['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403

    if order:
        return jsonify({
            'id': order.id,
            'user_id': order.user_id,
            'status': order.status,
            'note': order.note,
            'total': order.total,
            'order_details': [{
                'product_id': order_detail.product_id,
                'price': order_detail.price,
                'quantity': order_detail.quantity,
            } for order_detail in order.order_details],
            'created_at': order.created_at,
            'updated_at': order.updated_at,
            'transaction_id': order.transaction_id,
        }), 200
    return jsonify({'error': 'Order not found'}), 404

@order_blueprint.route('/user', methods=['GET'])
@token_required
def get_user_orders():
    """ API để lấy danh sách các hóa đơn của user """
    user_id = AuthService.decode_jwt_from_cookie()[0]['id']
    page = int(request.args.get('page', 1))  # Mặc định là trang 1
    per_page = int(request.args.get('per_page', 10))  
    status = request.args.get('status', None)
    time = request.args.get('time', None)
    order_id = request.args.get('order_id', None)
    orders = OrderService.get_order_by_user_id_and_params(user_id=user_id, 
                                                          status=status, 
                                                          time=time, 
                                                          order_id=order_id, 
                                                          page=page, 
                                                          per_page=per_page)
    return jsonify([{
                'id': order.id,
                'user_id': order.user_id,
                'status': order.status,
                'note': order.note,
                'total': order.total,
                'order_details': [{
                    'product_id': order_detail.product_id,
                    'product_name': order_detail.product.name,
                    'product_price': order_detail.product.price,
                    'product_image': order_detail.product.image.split(',')[0],
                    'price': order_detail.price,
                    'quantity': order_detail.quantity,
                } for order_detail in order.details],
                'created_at': order.created_at,
                'updated_at': order.updated_at,
                'transaction_id': order.transaction_id,
            } for order in orders]), 200

@order_blueprint.route('/create', methods=['POST'])
@token_required
def create_order():
    """ API để tạo hóa đơn mới """
    user_id = AuthService.decode_jwt_from_cookie()[0]['id']
    data = request.json
    cart_items = data.get("cartItems", [])
    name = data.get("name")
    phone = data.get("phone")
    email = data.get("email")
    order_info = data.get("order_info")
    address = data.get("address")

    total_amount = sum(
    (cart_item.get('product') or {}).get("price", 0) * cart_item.get("quantity", 1)
    for cart_item in cart_items
)
    
    if not all([cart_items, name, phone, email, address]):
        return jsonify({"error": "Missing required parameters"}), 400
    
    if cart_items == []:
        return jsonify({"error": "Cart is empty"}), 400

    new_address = None

    if address.get("id"):
        address_id = address.get("id")
        new_address = AddressService.get_address_by_id(address_id)
        if not new_address:
            return jsonify({'error': 'Address not found'}), 404
    else:
        new_address = AddressService.create_address(user_id, 
                                                    address.get("address_line"), 
                                                    address.get("city"), 
                                                    address.get("country"),
                                                    address.get("postal_code"))

    new_order = OrderService.create_order(
        user_id=user_id,
        name=name,
        phone=phone,
        email=email,
        status="pending",
        note=order_info,
        address_id=new_address.id,
        total=total_amount,
    )

    CartService.clear_user_cart(user_id)

    for cart_item in cart_items:
        OrderService.create_order_detail(new_order.id, cart_item.get("product").get("id"), 
                                         cart_item.get("product").get("price"), 
                                         cart_item.get("quantity"))
        ProductService.update_product_quantity_and_buyturn(cart_item.get("product").get("id"),
                                                            cart_item.get("quantity"))

    if new_order:
        return jsonify({
            'id': new_order.id,
            'user_id': new_order.user_id,
            'status': new_order.status,
            'note': new_order.note,
            'total': new_order.total,
            'created_at': new_order.created_at,
            'updated_at': new_order.updated_at,
            'transaction_id': new_order.transaction_id,
        }), 200
    return jsonify({'error': 'Create order failed'}), 400

@order_blueprint.route('/update/<int:order_id>', methods=['PUT'])
@admin_required
def update_order(order_id):
    """ API để cập nhật thông tin hóa đơn """
    data = request.json
    order = OrderService.get_order_by_id(order_id)
    status = data.get('status') or None
    note = data.get('note') or None

    if not order:
        return jsonify({'error': 'Order not found'}), 404

    updated_order = OrderService.update_order(order_id, status, note)

    if updated_order:
        return jsonify({
                'id': order.id,
                'user_id': order.user_id,
                'status': order.status,
                'note': order.note,
                'total': order.total,
                'order_details': [{
                    'product_id': order_detail.product_id,
                    'product_name': order_detail.product.name,
                    'product_price': order_detail.product.price,
                    'product_image': order_detail.product.image.split(',')[0],
                    'price': order_detail.price,
                    'quantity': order_detail.quantity,
                } for order_detail in order.details],
                'created_at': order.created_at,
                'updated_at': order.updated_at,
                'transaction_id': order.transaction_id,
            }), 200
    return jsonify({'error': 'Update order failed'}), 400

@order_blueprint.route('/<int:order_id>/cancel', methods=['PUT'])
@token_required
def cancel_order(order_id):
    """ API để hủy hóa đơn """
    user_id = AuthService.decode_jwt_from_cookie()[0]['id']
    order = OrderService.get_order_by_id(order_id)
    if order and order.user_id == user_id:
        updated_order = OrderService.cancel_order(order_id)
        if updated_order:
             return jsonify({
                'id': order.id,
                'user_id': order.user_id,
                'status': order.status,
                'note': order.note,
                'total': order.total,
                'order_details': [{
                    'product_id': order_detail.product_id,
                    'product_name': order_detail.product.name,
                    'product_price': order_detail.product.price,
                    'product_image': order_detail.product.image.split(',')[0],
                    'price': order_detail.price,
                    'quantity': order_detail.quantity,
                } for order_detail in order.details],
                'created_at': order.created_at,
                'updated_at': order.updated_at,
                'transaction_id': order.transaction_id,
            }), 200
        return jsonify({'error': 'Cancel order failed'}), 400
    return jsonify({'error': 'Unauthorized'}), 403

@order_blueprint.route('/delete/<int:order_id>', methods=['DELETE'])
@admin_required
def delete_order(order_id):
    """ API để xóa hóa đơn """
    if OrderService.delete_order(order_id):
        return jsonify({'message': 'Delete order successful'}), 200
    return jsonify({'error': 'Delete order failed'}), 400



