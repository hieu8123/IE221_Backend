from configs.database_configs import db
from app.models.banner import Banner
from datetime import datetime

class BannerService:
    @staticmethod
    def create_banner(product_id,image, name, status):
        new_banner = Banner(
            product_id=product_id,
            image=image,
            name=name,
            status=status,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(new_banner)
        db.session.commit()
        return new_banner

    @staticmethod
    def get_all_banners():
        return Banner.query.all()

    @staticmethod
    def get_banner_by_id(banner_id):
        return Banner.query.get(banner_id)

    @staticmethod
    def update_banner(banner_id,product_id, image, name, status):
        banner = Banner.query.get(banner_id)
        if banner:
            banner.product_id = product_id
            banner.image = image
            banner.name = name
            banner.status = status
            banner.updated_at = datetime.utcnow()
            db.session.commit()
            return banner
        return None

    @staticmethod
    def delete_banner(banner_id):
        banner = Banner.query.get(banner_id)
        if banner:
            db.session.delete(banner)
            db.session.commit()
            return True
        return False
