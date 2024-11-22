from app.configs.database_configs import db
from app.models.user import User
from datetime import datetime

class UserService:
    @staticmethod
    def create_user(email, password, name, role, avatar, phone):
        new_user = User(
            email=email,
            password=password,
            name=name,
            role=role,
            avatar=avatar,
            phone=phone,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(new_user)
        db.session.commit()
        return new_user

    @staticmethod
    def get_all_users():
        return User.query.all()

    @staticmethod
    def get_user_by_id(user_id):
        return User.query.get(user_id)

    @staticmethod
    def update_user(user_id, email, password, name, role, avatar, phone):
        user = User.query.get(user_id)
        if user:
            user.email = email
            user.password = password
            user.name = name
            user.role = role
            user.avatar = avatar
            user.phone = phone
            user.updated_at = datetime.utcnow()
            db.session.commit()
            return user
        return None

    @staticmethod
    def delete_user(user_id):
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return True
        return False
