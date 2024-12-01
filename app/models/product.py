from app.configs.database_configs import db
from datetime import datetime

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=True)
    price = db.Column(db.Integer, nullable=True)
    oldprice = db.Column(db.Integer, nullable=True)
    image = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    specification = db.Column(db.Text, nullable=True)
    buyturn = db.Column(db.Integer, nullable=False, default=0)
    quantity = db.Column(db.Integer, nullable=True)
    brand_id = db.Column(db.Integer, db.ForeignKey('brands.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    brand = db.relationship('Brand', back_populates='products')
    banner = db.relationship('Banner', back_populates='product', cascade="all, delete-orphan")
    category = db.relationship('Category', back_populates='products')
    feedbacks = db.relationship('Feedback', back_populates='product', cascade="all, delete-orphan")
    news = db.relationship('News', back_populates='product', cascade="all, delete-orphan")
    order_details = db.relationship('OrderDetail', back_populates='product', cascade="all, delete-orphan")
    carts = db.relationship('Cart', back_populates='product', cascade="all, delete-orphan")

    def to_dict(self):
        images = self.image.split(',') if self.image else []
        return {'id': self.id,
                'name': self.name,  
                'category': self.category.name,
                'brand': self.brand.name,
                'price': self.price,
                'oldprice': self.oldprice,
                'images': images ,
                'description': self.description,
                'specification': self.specification,
                'buyturn': self.buyturn,
                'quantity': self.quantity,
                'created_at': self.created_at,
                'updated_at': self.updated_at}
    
