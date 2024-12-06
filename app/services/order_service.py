from app.configs.database_configs import db
from app.models.order import Order, OrderDetail
from datetime import datetime

class OrderService:
    @staticmethod
    def create_order(user_id, note, total, status='pending',name=None, phone=None, email=None, address_id=None):
        new_order = Order(
            user_id=user_id,
            status=status,
            name=name,
            phone=phone,
            email=email,
            note=note,
            address_id=address_id,
            total=total,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(new_order)
        db.session.commit()
        return new_order

    @staticmethod
    def get_all_orders():
        return Order.query.all()
    
    @staticmethod
    def get_all_orders_page(page=1, per_page=10):
        return Order.query.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_order_by_id(order_id):
        return Order.query.get(order_id)
    
    @staticmethod
    def get_orders_by_user_id(user_id):
        return Order.query.filter_by(user_id=user_id).all()
    
    @staticmethod
    def get_order_by_user_id_page(user_id, page=1, per_page=10):
        return Order.query.filter_by(user_id=user_id).paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def update_order(order_id, status=None, note=None):
        order = Order.query.get(order_id)
        if order:
            order.status = status or order.status
            order.note = note or order.note
            order.updated_at = datetime.utcnow()
            db.session.commit()
            return order
        return None
    
    @staticmethod
    def update_transaction_id(transaction_id, order_id):
        order = Order.query.get(order_id)
        if order:
            order.transaction_id = transaction_id
            order.updated_at = datetime.utcnow()
            db.session.commit()
            return order
    
    @staticmethod
    def update_order_status(order_id, status):
        order = Order.query.get(order_id)
        if order:
            order.status = status
            order.updated_at = datetime.utcnow()
            db.session.commit()
            return order
        return None

    @staticmethod
    def delete_order(order_id):
        order = Order.query.get(order_id)
        if order:
            for order_detail in order.order_details:
                db.session.delete(order_detail)
            db.session.delete(order)
            db.session.commit()
            return True
        return False

    @staticmethod
    def create_order_detail(order_id, product_id, price, quantity):
        new_order_detail = OrderDetail(
            order_id=order_id,
            product_id=product_id,
            price=price,
            quantity=quantity,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(new_order_detail)
        db.session.commit()
        return new_order_detail

    @staticmethod
    def get_order_details_by_order_id(order_id):
        return OrderDetail.query.filter_by(order_id=order_id).all()
