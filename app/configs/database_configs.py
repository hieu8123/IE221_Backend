from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.exc import OperationalError

db = SQLAlchemy()
migrate = Migrate()

def init_database(app):
    db.init_app(app)
    migrate.init_app(app, db)

def check_db_connection(app):
    with app.app_context():  # Đảm bảo rằng ta đang trong ứng dụng context
        try:
            # Dùng trực tiếp db.engine để kiểm tra kết nối
            with db.engine.connect():
                print("Database connection successful!")
        except OperationalError as e:
            print("Error: Unable to connect to the database")
            print(str(e))
