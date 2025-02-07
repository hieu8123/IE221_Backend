from app.configs.database_configs import db
from datetime import datetime

class Address(db.Model):
    __tablename__ = 'addresses'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    address_line = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False, default='Vietnam')
    postal_code = db.Column(db.String(20), nullable=True)
    note = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship with User
    user = db.relationship('User', back_populates='addresses')
    orders = db.relationship('Order', back_populates='address')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'address_line': self.address_line,
            'city': self.city,
            'country': self.country,
            'postal_code': self.postal_code,
            'note': self.note,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
