from app.configs.database_configs import db
from app.models.user import User
from datetime import datetime

class UserService:
    @staticmethod
    def create_user(email, password, name, role, avatar=None, phone=None):
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
    def update_user(user_id, email, name, avatar, phone, role=None, password=None):
        user = User.query.get(user_id)

        if user:
            # Kiểm tra kiểu dữ liệu
            if not isinstance(email, str):
                raise TypeError("email must be a string")
            if not isinstance(name, str):
                raise TypeError("name must be a string")
            if not isinstance(avatar, str):
                raise TypeError("avatar must be a string")
            if not isinstance(phone, str):
                raise TypeError("phone must be a string")
            if role and not isinstance(role, str):
                raise TypeError("role must be a string")
            if password and not isinstance(password, str):
                raise TypeError("password must be a string")

        if user:
            # Kiểm tra xem có thay đổi hay không
            has_changes = False

            if user.email != email:
                user.email = email
                has_changes = True
            if password and user.password != password:
                user.password = password
                has_changes = True
            if user.name != name:
                user.name = name
                has_changes = True
            if role and user.role != role:
                user.role = role
                has_changes = True
            if user.avatar != avatar:
                user.avatar = avatar
                has_changes = True
            if user.phone != phone:
                user.phone = phone
                has_changes = True

            # Nếu có thay đổi thì cập nhật thời gian và commit
            if has_changes:
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
