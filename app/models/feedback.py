from app.configs.database_configs import db
from datetime import datetime

class Feedback(db.Model):
    __tablename__ = 'feedbacks'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    star = db.Column(db.Integer, nullable=True)
    content = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    product = db.relationship('Product', back_populates='feedbacks')
    user = db.relationship('User', back_populates='feedbacks')
