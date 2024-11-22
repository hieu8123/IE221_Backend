from app.configs.database_configs import db
from app.models.news import News, NewsDetail
from datetime import datetime

class NewsService:
    @staticmethod
    def create_news(product_id,title, content, image):
        new_news = News(
            product_id=product_id,
            title=title,
            content=content,
            image=image,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(new_news)
        db.session.commit()
        return new_news

    @staticmethod
    def get_all_news():
        return News.query.all()

    @staticmethod
    def get_news_by_id(news_id):
        return News.query.get(news_id)

    @staticmethod
    def update_news(news_id,product_id, title, content, image):
        news = News.query.get(news_id)
        if news:
            news.product_id = product_id
            news.title = title
            news.content = content
            news.image = image
            news.updated_at = datetime.utcnow()
            db.session.commit()
            return news
        return None

    @staticmethod
    def delete_news(news_id):
        news = News.query.get(news_id)
        if news:
            db.session.delete(news)
            db.session.commit()
            return True
        return False
