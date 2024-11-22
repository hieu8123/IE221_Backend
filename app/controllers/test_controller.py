from flask import Blueprint, jsonify, request, make_response
from werkzeug.security import generate_password_hash
from app.middlewares.auth import token_required, admin_required


# Tạo Blueprint cho module auth
test_blueprint = Blueprint('test', __name__)

@test_blueprint.route('/login', methods=['GET'])
@token_required
def test():
    return jsonify({'message': 'u are logged in!'}), 200

@test_blueprint.route('/admin', methods=['GET'])
@admin_required
def test_admin():
    return jsonify({'message': 'u are admin!'}), 200


