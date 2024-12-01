from flask import Blueprint, jsonify, request, make_response
from app.services.cart_service import CartService
from app.services.user_service import UserService
from app.middlewares.auth import token_required, admin_required
from app.services.auth_serivce import AuthService

# Tạo Blueprint cho module auth
cart_blueprint = Blueprint('cart', __name__)

@cart_blueprint.route('/user', methods=['GET'])
@token_required
def get_user_cart():
    """ API để lấy giỏ hàng của người dùng """
    user_id = AuthService.decode_jwt_from_cookie()[0]['id']

    carts = CartService.get_user_cart(user_id)
    if not carts:
        return jsonify([]), 200
    
    products = [cart.product for cart in carts]

    return jsonify([{
        'product': product.to_dict(),
        'id': cart.id,
        'quantity': cart.quantity
    } for product, cart in zip(products, carts)]), 200

@cart_blueprint.route('/product-cart', methods=['GET'])
@token_required
def get_products_in_user_cart():
    """ API để lấy thông tin sản phẩm trong giỏ hàng của người dùng """
    user_id = AuthService.decode_jwt_from_cookie()[0]['id']

    user = UserService.get_user_by_id(user_id)
    products = [cart.product for cart in user.carts]

    return jsonify([{
        'product': product.to_dict(),
        'id': cart.id,
        'quantity': cart.quantity
    } for product, cart in zip(products, user.carts)]), 200



@cart_blueprint.route('/sync', methods=['POST', 'PUT'])
@token_required
def sync_user_cart():
    """ API để cập nhật giỏ hàng của người dùng """
    user_id = AuthService.decode_jwt_from_cookie()[0]['id']
    product_in_cart = request.json.get('product_in_cart', [])

    print(f'Product in cart: {len(product_in_cart)}')

    if len(product_in_cart) == 0:
        print(f'Clearing user cart {user_id}')
        CartService.clear_user_cart(user_id)
        return jsonify({'message': 'User cart cleared'}), 200
    
    CartService.update_user_cart(user_id, product_in_cart)

    return jsonify({'message': 'User cart updated successfully'}), 200

