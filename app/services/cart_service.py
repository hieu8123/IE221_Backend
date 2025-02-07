from app.configs.database_configs import db
from app.models.cart import Cart
from datetime import datetime
from sqlalchemy.orm.exc import NoResultFound


class CartService:
    @staticmethod
    def get_user_cart(user_id):
        return Cart.query.filter_by(user_id=user_id).all()
    
    @staticmethod
    def update_user_list_cart(user_id, product_in_cart):
        Cart.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        for product in product_in_cart:
            new_cart = Cart(
                user_id=user_id,
                product_id=product['product_id'],
                quantity=product['quantity'],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(new_cart)
            db.session.commit()
        return True
    @staticmethod
    def update_user_cart(user_id, product_in_cart):
        # Lấy danh sách sản phẩm hiện tại trong giỏ hàng của người dùng
        current_cart = Cart.query.filter_by(user_id=user_id).all()
        current_product_ids = [cart.product_id for cart in current_cart]  # Lấy danh sách product_id hiện có trong giỏ hàng

        # Lấy danh sách product_id từ giỏ hàng được gửi lên
        new_product_ids = [product['product_id'] for product in product_in_cart]

        # Xóa sản phẩm không còn trong giỏ hàng (sản phẩm không có trong new_product_ids)
        for cart in current_cart:
            if cart.product_id not in new_product_ids:
                db.session.delete(cart)  # Xóa sản phẩm không còn trong giỏ hàng

        # Cập nhật hoặc thêm sản phẩm mới vào giỏ hàng
        for product in product_in_cart:
            cart = Cart.query.filter_by(user_id=user_id, product_id=product['product_id']).first()
            if cart:
                try:
                    # Cập nhật sản phẩm đã có trong giỏ
                    cart.quantity = product['quantity']
                    cart.updated_at = datetime.utcnow()
                except NoResultFound:
                    db.session.rollback()
                    continue
            else:
                # Thêm sản phẩm mới vào giỏ
                new_cart = Cart(
                    user_id=user_id,
                    product_id=product['product_id'],
                    quantity=product['quantity'],
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.session.add(new_cart)

        # Commit all changes at once to ensure consistency
        db.session.commit()

        return True
    @staticmethod
    def clear_user_cart(user_id):
        Cart.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        return True