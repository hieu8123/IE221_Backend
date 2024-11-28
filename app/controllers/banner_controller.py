from flask import Blueprint, jsonify
from app.services.banner_service import BannerService


# Tạo Blueprint cho module auth
banner_blueprint = Blueprint('banner', __name__)

@banner_blueprint.route('/', methods=['GET'])
def get_all_banner():
    """
    API để lấy danh sách các banner quảng cáo
    """
    banners = BannerService.get_all_banners()
    return jsonify([{'id': banner.id,
                     'image': banner.image,
                    'name': banner.name,
                    'product_id': banner.product_id,
                        'status': banner.status,
                     'created_at': banner.created_at,
                     'updated_at': banner.updated_at} 
                    for banner in banners]), 200



