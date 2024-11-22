from app.configs.database_configs import db
from app.models.order import Order, OrderDetail
from datetime import datetime

class OrderService:
    @staticmethod
    def create_order(user_id, status, note, total):
        new_order = Order(
            user_id=user_id,
            status=status,
            note=note,
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
    def get_order_by_id(order_id):
        return Order.query.get(order_id)

    @staticmethod
    def update_order(order_id, status, note, total):
        order = Order.query.get(order_id)
        if order:
            order.status = status
            order.note = note
            order.total = total
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
