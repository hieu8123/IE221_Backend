from app.configs.database_configs import db
from app.models.product import Product
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.dialects import mysql

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
    def get_products(page, per_page, name=None, sort_by=None, sort_order='asc', **kwargs):
        """
        Truy vấn sản phẩm với các tiêu chí linh hoạt (lọc, tìm kiếm, phân trang, và sắp xếp).
        - page: Số trang.
        - per_page: Số sản phẩm mỗi trang.
        - name: Tên sản phẩm (tìm kiếm theo LIKE).
        - sort_by: Trường cần sắp xếp ('price', 'created_at').
        - sort_order: Thứ tự sắp xếp ('asc' hoặc 'desc').
        - kwargs: Các tham số lọc khác như category_id, brand_id.
        """
        query = Product.query

        # Tìm kiếm theo tên sản phẩm
        if name:
            name = name.strip().lower()
            query = query.filter(func.lower(Product.name).like(f"%{name}%"))

        # Lọc theo các điều kiện khác
        for key, value in kwargs.items():
            if value is not None:  # Chỉ lọc khi giá trị không phải là None
                print(key, value)
                query = query.filter(getattr(Product, key) == value)

        # Các trường được phép sắp xếp
        allowed_sort_fields = ['price', 'created_at']
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

        # In ra query SQL để kiểm tra
        print(str(query.statement.compile(dialect=mysql.dialect())))

        # Phân trang
        return query.paginate(page=page, per_page=per_page, error_out=False)



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
    def delete_product(product_id):
        product = Product.query.get(product_id)
        if product:
            db.session.delete(product)
            db.session.commit()
            return True
        return False
