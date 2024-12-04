from flask import Blueprint, jsonify, request, make_response, g
from app.services.auth_serivce import AuthService
from app.services.user_service import UserService
from app.services.address_service import AddressService
from app.middlewares.auth import token_required

# Tạo Blueprint cho module auth
user_blueprint = Blueprint('user', __name__)


@user_blueprint.route('/detail/<int: user_id>', methods=['GET'])
@token_required
def user_detail(user_id):
    """Xem thông tin người dùng"""
    if(user_id != g.token.get('id')):
        if g.token.get('role') != 'admin':
            return jsonify({'message': 'Unauthorized'}), 403

    user = UserService.get_user_by_id(user_id)

    return jsonify(user.to_dict()), 200

@user_blueprint.route('/update/<int: user_id>', methods=['PUT'])
@token_required
def user_update(user_id):
    """Cập nhật thông tin người dùng"""
    if(user_id != g.token.get('id')):
        if g.token.get('role') != 'admin':
            return jsonify({'message': 'Unauthorized'}), 403

    email = request.json.get('email')
    password = request.json.get('password')
    name = request.json.get('name')
    role = request.json.get('role')
    avatar = request.json.get('avatar')
    phone = request.json.get('phone')

    updated_user = UserService.update_user(user_id, email, password, name, role, avatar, phone)
    if not updated_user:
        return jsonify({'message': 'Update failed'}), 500

    return jsonify(updated_user.to_dict()), 200

@user_blueprint.route('/add-address', methods=['POST'])
@token_required
def add_address():
    """Thêm địa chỉ người dùng"""
    user_id = g.token.get('id')
    address_line = request.json.get('address_line')
    city = request.json.get('city')
    contry = request.json.get('contry')
    postal_code = request.json.get('postal_code')
    note = request.json.get('note')



    new_address = AddressService.create_address(user_id,address_line,city,contry,postal_code,note)
    if not new_address:
        return jsonify({'message': 'Add address failed'}), 500

    return jsonify(new_address.to_dict()), 200

@user_blueprint.route('/update-address/<int: address_id>', methods=['PUT'])
@token_required
def update_address(address_id):
    """Cập nhật địa chỉ người dùng"""
    user_id = g.token.get('id')
    address_line = request.json.get('address_line')
    city = request.json.get('city')
    contry = request.json.get('contry')
    postal_code = request.json.get('postal_code')
    note = request.json.get('note')

    address = AddressService.get_address_by_id(address_id)
    if not address:
        return jsonify({'message': 'Address not found'}), 404
    
    if address.user_id != user_id:
        return jsonify({'message': 'You are not allowed to update this address'}), 403

    updated_address = AddressService.update_address(address_id,user_id,address_line,city,contry,postal_code,note)
    if not updated_address:
        return jsonify({'message': 'Update address failed'}), 500

    return jsonify(updated_address.to_dict()), 200


@user_blueprint.route('/delete-address/<int: address_id>', methods=['DELETE'])
@token_required
def delete_address(address_id):
    """Xóa địa chỉ người dùng"""
    user_id = g.token.get('id')

    address = AddressService.get_address_by_id(address_id)
    if not address:
        return jsonify({'message': 'Address not found'}), 404
    
    if address.user_id != user_id:
        return jsonify({'message': 'You are not allowed to delete this address'}), 403

    if AddressService.delete_address(address_id):
        return jsonify({'message': 'Delete address successful'}), 200
    return jsonify({'message': 'Delete address failed'}), 500