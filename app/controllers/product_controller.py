from flask import Blueprint, jsonify, request, make_response
from werkzeug.security import generate_password_hash
from app.middlewares.auth import token_required, admin_required
from app.services.product_service import ProductService
import datetime


# Tạo Blueprint cho module auth
product_blueprint = Blueprint('product', __name__)

@product_blueprint.route('/filter', methods=['GET'])
def get_products():
    """
    API để lấy danh sách sản phẩm với phân trang và các bộ lọc linh hoạt.
    """
    # Lấy tham số phân trang
    page = int(request.args.get('page', 1))  # Mặc định là trang 1
    per_page = int(request.args.get('per_page', 10))  # Mặc định 10 sản phẩm/trang

    # Lấy các tham số bộ lọc (name, category_id, brand_id)
    name = request.args.get('name')  # Tìm kiếm theo tên
    max_price = request.args.get('max_price') # Lọc theo khoảng giá
    min_price = request.args.get('min_price') # Lọc theo khoảng giá
    price_range = None
    if max_price and min_price:
        price_range = min_price + '-' + max_price
    category_id = request.args.get('category_id', type=int)  # Lọc theo category_id
    brand_id = request.args.get('brand_id', type=int)  # Lọc theo brand_id

    # Lấy tham số sắp xếp
    sort_by = request.args.get('sort_by')  # 'price' hoặc 'created_at' hoặc 'buyturn'
    sort_order = request.args.get('sort_order', 'asc')  # 'asc' hoặc 'desc'

    # Gọi service để truy vấn sản phẩm
    products_paginated = ProductService.get_products(
        page=page,
        per_page=per_page,
        name=name,
        price_range=price_range,
        category_id=category_id,
        brand_id=brand_id,
        sort_by=sort_by,
        sort_order=sort_order
    )

    # Chuẩn bị dữ liệu trả về
    return jsonify({
        'page': products_paginated.page,
        'per_page': products_paginated.per_page,
        'total': products_paginated.total,
        'total_pages': products_paginated.pages,
        'products': [
            {'id': product.id,
                'name': product.name,  
                'category': product.category.name,
                'brand': product.brand.name,
                'price': product.price,
                'oldprice': product.oldprice,
                'images': product.image.split(',') if product.image else [],
                'specification': product.specification,
                'buyturn': product.buyturn,
                'quantity': product.quantity,
                'created_at': product.created_at,
                'updated_at': product.updated_at}

            for product in products_paginated.items
        ]
    })

@product_blueprint.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """
    API để lấy thông tin chi tiết của một sản phẩm.
    """
    # Gọi service để lấy thông tin sản phẩm
    product = ProductService.get_product_by_id(product_id)

    if not product:
        return jsonify({'message': 'Product not found!'}), 404

    # Trả về thông tin sản phẩm
    return jsonify(product.to_dict())

@product_blueprint.route('/create', methods=['POST'])
@admin_required
def create_product():
    """
    API để tạo sản phẩm mới.
    """
    # Lấy thông tin sản phẩm từ body của request
    product_data = request.json

    # Gọi service để tạo sản phẩm
    new_product = ProductService.create_product(
                    name=product_data['name'],
                    price=product_data['price'],
                    oldprice=product_data['oldprice'],
                    image=product_data['image'],
                    description=product_data['description'],
                    specification=product_data['specification'],
                    buyturn=product_data.get('buyturn', 0), 
                    quantity=product_data.get('quantity'),
                    brand_id=product_data['brand_id'],
                    category_id=product_data['category_id'],
                )
    
    if not new_product:
        return jsonify({'message': 'Create product failed!'}), 400
    
    # Trả về thông tin sản phẩm vừa tạo
    return jsonify(new_product.to_dict())

@product_blueprint.route('/<int:product_id>/update', methods=['PUT'])
@admin_required
def update_product(product_id):
    """
    API để cập nhật thông tin sản phẩm.
    """
    # Lấy thông tin sản phẩm từ body của request
    product_data = request.json

    # Gọi service để cập nhật thông tin sản phẩm
    updated_product = ProductService.update_product(
                        product_id=product_id,
                        name=product_data['name'],
                        price=product_data['price'],
                        oldprice=product_data['oldprice'],
                        image=product_data['image'],
                        description=product_data['description'],
                        specification=product_data['specification'],
                        buyturn=product_data.get('buyturn', 0), 
                        quantity=product_data.get('quantity'),
                        brand_id=product_data['brand_id'],
                        category_id=product_data['category_id'],
                    )
    
    if not updated_product:
        return jsonify({'message': 'Product not found!'}), 404
    
    # Trả về thông tin sản phẩm vừa cập nhật
    return jsonify(updated_product.to_dict())

@product_blueprint.route('/<int:product_id>/delete', methods=['DELETE'])
@admin_required
def delete_product(product_id):
    """
    API để xóa sản phẩm.
    """
    # Gọi service để xóa sản phẩm
    deleted_product = ProductService.delete_product(product_id)

    if not deleted_product:
        return jsonify({'message': 'Product not found!'}), 404
    
    # Trả về thông báo xóa thành công
    return jsonify({'message': 'Delete product successfully!'})

@product_blueprint.route('/<int:product_id>/recommend', methods=['get'])
def recommend_products(product_id):
    """
    API để gợi ý sản phẩm liên quan dựa trên sản phẩm đang xem.
    """
    # Gọi service để gợi ý sản phẩm liên quan
    related_products = ProductService.get_recommend_products(product_id)

    # Trả về danh sách sản phẩm liên quan
    return jsonify([
        product.to_dict()
        for product in related_products
    ]), 200
