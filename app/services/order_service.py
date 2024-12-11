from app.configs.database_configs import db
from app.models.order import Order, OrderDetail
from app.services.product_service import ProductService
from datetime import datetime, timedelta

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
    def get_order_by_user_id_and_params(user_id, status=None, time=None, order_id=None, page=1, per_page=10):
        query = Order.query.filter(Order.user_id == user_id)

        # Filter by status
        if status and status != 'all':
            query = query.filter(Order.status == status)

        # Filter by time range
        if time:
            now = datetime.utcnow()
            time_mapping = {
                'day': now.replace(hour=0, minute=0, second=0, microsecond=0),
                'week': (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0),
                'month': now.replace(day=1, hour=0, minute=0, second=0, microsecond=0),
                '6months': (now - timedelta(days=6 * 30)).replace(hour=0, minute=0, second=0, microsecond=0),
                'year': now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0),
                'all': None
            }
            start_time = time_mapping.get(time)

            if start_time:
                query = query.filter(Order.created_at >= start_time)

        # Filter by order_id
        if order_id:
            query = query.filter(Order.id == order_id)

        # Paginate the results
        return query.paginate(page=page, per_page=per_page, error_out=False)


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
    def cancel_order(order_id):
        order = Order.query.get(order_id)
        if order and order.status in ['pending', 'awaiting payment']:
            order.status = 'cancelled'
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
        product = ProductService.get_product_by_id(product_id)
        if not product:
            raise Exception("Product not found")
        if product.quantity < quantity:
            raise Exception("Not enough product in stock")
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
