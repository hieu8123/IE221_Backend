from flask import Blueprint, jsonify, request, make_response
from app.services.brand_service import BrandService


# Tạo Blueprint cho module auth
brand_blueprint = Blueprint('brand', __name__)

@brand_blueprint.route('/', methods=['GET'])
def get_all_brands():
    """ API để lấy danh sách các thương hiệu """
    brands = BrandService.get_all_brands()
    return jsonify([{'id': brand.id,
                     'name': brand.name,
                     'image': brand.image,
                     'created_at': brand.created_at,
                     'updated_at': brand.updated_at} 
                    for brand in brands]), 200






