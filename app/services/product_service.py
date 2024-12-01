from app.configs.database_configs import db
from app.models.product import Product
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.dialects import mysql
import pandas as pd
import numpy as np
from app.utils.recommend import load_pipeline
import traceback





class ProductService:


    @staticmethod
    def create_product(name, price, oldprice, image, description, specification, buyturn, quantity, brand_id, category_id):
        new_product = Product(
            name=name,
            price=price,
            oldprice=oldprice,
            image=image,
            description=description,
            specification=specification,
            buyturn=buyturn,
            quantity=quantity,
            brand_id=brand_id,
            category_id=category_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(new_product)
        db.session.commit()
        return new_product

    @staticmethod
    def get_all_products():
        return Product.query.all()

    @staticmethod
    def get_products(page, per_page, name=None,price_range=None, sort_by=None, sort_order='asc', **kwargs):
        """
        Truy vấn sản phẩm với các tiêu chí linh hoạt (lọc, tìm kiếm, phân trang, và sắp xếp).
        - page: Số trang.
        - per_page: Số sản phẩm mỗi trang.
        - name: Tên sản phẩm (tìm kiếm theo LIKE).
        - price_range: Khoảng giá (min-max).
        - brand_id: ID thương hiệu.
        - category_id: ID danh mục.
        - sort_by: Trường cần sắp xếp ('price', 'created_at').
        - sort_order: Thứ tự sắp xếp ('asc' hoặc 'desc').
        - kwargs: Các tham số lọc khác như category_id, brand_id.
        """
        query = Product.query

        # Tìm kiếm theo tên sản phẩm
        if name:
            name = name.strip().lower()
            query = query.filter(func.lower(Product.name).like(f"%{name}%"))
        
        if price_range:
            price_range = price_range.split('-')
            if len(price_range) == 2:
                try:
                    min_price = int(price_range[0])
                    max_price = int(price_range[1])
    
                    query = query.filter(Product.price >= min_price, Product.price <= max_price)
                except ValueError:
                    raise ValueError("Invalid price values. Please ensure they are numeric.")
            
            else:
                raise ValueError("Invalid price range format. Please use 'min-max' format.")   

        # Lọc theo các điều kiện khác
        for key, value in kwargs.items():
            if value is not None:  # Chỉ lọc khi giá trị không phải là None
                query = query.filter(getattr(Product, key) == value)

        # Các trường được phép sắp xếp
        allowed_sort_fields = ['price','buyturn', 'created_at']
        allowed_sort_orders = ['asc', 'desc']

        # Kiểm tra và áp dụng sắp xếp
        if sort_by and sort_by in allowed_sort_fields:
            sort_column = getattr(Product, sort_by)
            if sort_order in allowed_sort_orders:
                if sort_order == 'desc':
                    query = query.order_by(sort_column.desc())
                else:
                    query = query.order_by(sort_column.asc())
            else:
                raise ValueError(f"Invalid sort_order: {sort_order}. Allowed values are {allowed_sort_orders}")
        elif sort_by:
            raise ValueError(f"Invalid sort_by: {sort_by}. Allowed fields are {allowed_sort_fields}")


        # Phân trang
        return query.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_recommend_products(product_id):
        try:
            pipeline = load_pipeline()
            products = db.session.query(Product.id, Product.brand_id, Product.category_id, Product.price).all()
            df = pd.DataFrame(products, columns=['id', 'brand_id', 'category_id', 'price'])

            if product_id not in df['id'].values:
                raise ValueError(f"Product with id {product_id} not found.")

            product_index = df[df['id'] == product_id].index[0]
                    # Trích xuất đặc trưng của sản phẩm
            product_features = df.iloc[product_index:product_index+1][['brand_id', 'category_id', 'price']]
        

            # Biến đổi đặc trưng đầu vào qua pipeline
            query_transformed = pipeline.named_steps['preprocessing'].transform(product_features)

            # Tìm kiếm hàng xóm gần nhất
            distances, indices = pipeline.named_steps['modeling'].kneighbors(query_transformed)

            # Lấy danh sách các sản phẩm tương tự với giới hạn
            similar_product_indices = indices[0]
            similar_products = df.iloc[similar_product_indices]  # Đảm bảo bạn đang thao tác trên DataFrame


            # Lấy ID của các sản phẩm tương tự và loại bỏ ID của sản phẩm gốc
            similar_product_ids = similar_products['id'].values
    
            similar_product_ids = [pid for pid in similar_product_ids if pid != product_id]

            # Truy vấn chi tiết thông tin sản phẩm từ cơ sở dữ liệu
            recommended_products = [Product.query.get(product_id) for product_id in similar_product_ids]

            return recommended_products

        
        except FileNotFoundError as e:
            print(e)
            return []
        
        except Exception as e:
            print("Lỗi xảy ra:")
            print(traceback.format_exc())
            return []

    @staticmethod
    def get_product_by_id(product_id):
        return Product.query.get(product_id)

    @staticmethod
    def update_product(product_id, name, price, oldprice, image, description, specification, buyturn, quantity, brand_id, category_id):
        product = Product.query.get(product_id)
        if product:
            product.name = name
            product.price = price
            product.oldprice = oldprice
            product.image = image
            product.description = description
            product.specification = specification
            product.buyturn = buyturn
            product.quantity = quantity
            product.brand_id = brand_id
            product.category_id = category_id
            product.updated_at = datetime.utcnow()
            db.session.commit()
            return product
        return None
    
    @staticmethod
    def update_product_quantity_and_buyturn(product_id, quantity=1):
        product = Product.query.get(product_id)
        if product:
            product.quantity -= quantity
            product.buyturn += quantity
            db.session.commit()
            return product
        return None

    @staticmethod
    def delete_product(product_id):
        product = Product.query.get(product_id)
        if product:
            db.session.delete(product)
            db.session.commit()
            return True
        return False
