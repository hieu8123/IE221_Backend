from app.configs.database_configs import db
from app.models.category import Category
from datetime import datetime

class CategoryService:
    @staticmethod
    def create_category(name, image):
        new_category = Category(
            name=name,
            image=image,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(new_category)
        db.session.commit()
        return new_category

    @staticmethod
    def get_all_categories():
        return Category.query.all()

    @staticmethod
    def get_category_by_id(category_id):
        return Category.query.get(category_id)

    @staticmethod
    def update_category(category_id, name, image):
        category = Category.query.get(category_id)
        if category:
            category.name = name
            category.image = image
            category.updated_at = datetime.utcnow()
            db.session.commit()
            return category
        return None

    @staticmethod
    def delete_category(category_id):
        category = Category.query.get(category_id)
        if category:
            db.session.delete(category)
            db.session.commit()
            return True
        return False
