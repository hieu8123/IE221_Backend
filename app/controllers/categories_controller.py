from flask import Blueprint, jsonify, request, make_response
from app.services.category_service import CategoryService
from app.middlewares.auth import token_required, admin_required


# Tạo Blueprint cho module auth
category_blueprint = Blueprint('categories', __name__)

@category_blueprint.route('/', methods=['GET'])
def get_app_categories():
    """ API để lấy danh sách các danh mục sản phẩm """
    categories = CategoryService.get_all_categories()
    return jsonify([{'id': category.id,
                     'name': category.name,
                     'image': category.image,
                     'created_at': category.created_at,
                     'updated_at': category.updated_at} 
                    for category in categories]), 200





