from app.configs.database_configs import db
from datetime import datetime

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.Integer, nullable=True)
    note = db.Column(db.Text, nullable=True)
    total = db.Column(db.Integer, nullable=True)
    transaction_id = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    details = db.relationship('OrderDetail', back_populates='order', cascade="all, delete-orphan")
    user = db.relationship('User', back_populates='orders')
    refund_request = db.relationship('RefundRequest', back_populates='order')


class OrderDetail(db.Model):
    __tablename__ = 'order_details'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    price = db.Column(db.Integer, nullable=True)
    quantity = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    order = db.relationship('Order', back_populates='details')
    product = db.relationship('Product', back_populates='order_details')
