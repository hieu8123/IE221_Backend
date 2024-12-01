from app.configs.database_configs import db
from app.models.brand import Brand
import datetime

class BrandService:
    @staticmethod
    def create_brand(name, image):
        new_brand = Brand(
            name=name,
            image=image,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(new_brand)
        db.session.commit()
        return new_brand

    @staticmethod
    def get_all_brands():
        return Brand.query.all()

    @staticmethod
    def get_brand_by_id(brand_id):
        return Brand.query.get(brand_id)

    @staticmethod
    def update_brand(brand_id, name, image):
        brand = Brand.query.get(brand_id)
        if brand:
            brand.name = name
            brand.image = image
            brand.updated_at = datetime.utcnow()
            db.session.commit()
            return brand
        return None

    @staticmethod
    def delete_brand(brand_id):
        brand = Brand.query.get(brand_id)
        if brand:
            db.session.delete(brand)
            db.session.commit()
            return True
        return False

