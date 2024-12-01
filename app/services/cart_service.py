from app.configs.database_configs import db
from app.models.cart import Cart
from datetime import datetime


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
        for product in product_in_cart:
            cart = Cart.query.filter_by(user_id=user_id, product_id=product['product_id']).first()
            if cart:
                cart.quantity = product['quantity']
                cart.updated_at = datetime.utcnow()
                db.session.commit()
            else:
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
    def clear_user_cart(user_id):
        Cart.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        return True