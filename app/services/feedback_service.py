from app.configs.database_configs import db
from app.models.feedback import Feedback
from datetime import datetime

class FeedbackService:
    @staticmethod
    def create_feedback(product_id, user_id, star, content):
        new_feedback = Feedback(
            product_id=product_id,
            user_id=user_id,
            star=star,
            content=content,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(new_feedback)
        db.session.commit()
        return new_feedback

    @staticmethod
    def get_all_feedbacks():
        return Feedback.query.all()

    @staticmethod
    def get_feedback_by_id(feedback_id):
        return Feedback.query.get(feedback_id)

    @staticmethod
    def update_feedback(feedback_id, star, content):
        feedback = Feedback.query.get(feedback_id)
        if feedback:
            feedback.star = star
            feedback.content = content
            feedback.updated_at = datetime.utcnow()
            db.session.commit()
            return feedback
        return None

    @staticmethod
    def delete_feedback(feedback_id):
        feedback = Feedback.query.get(feedback_id)
        if feedback:
            db.session.delete(feedback)
            db.session.commit()
            return True
        return False
