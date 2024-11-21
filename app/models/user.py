from app.configs.database_configs import db
from datetime import datetime
from .feedback import Feedback
from .order import Order

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=True)
    password = db.Column(db.String(255), nullable=True)
    name = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(50), default='ROLE_USER') 
    avatar = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    feedbacks = db.relationship('Feedback', back_populates='user', cascade="all, delete-orphan")
    orders = db.relationship('Order', back_populates='user', cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'avatar': self.avatar,
            'phone': self.phone,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
