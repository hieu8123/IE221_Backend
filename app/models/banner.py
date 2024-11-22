from app.configs.database_configs import db

from datetime import datetime

class Banner(db.Model):
    __tablename__ = 'banners'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    image = db.Column(db.Text, nullable=True)
    name = db.Column(db.String(255), nullable=True)
    status = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    product = db.relationship('Product', back_populates='banner')

    
