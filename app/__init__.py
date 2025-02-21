from flask import Flask
from app.configs.database_configs import init_database, check_db_connection
from app.configs.core_configs import Config
from flask_cors import CORS
from app.controllers.auth_controller import auth_blueprint
from app.controllers.test_controller import test_blueprint
from app.controllers.product_controller import product_blueprint
from app.controllers.payment_controller import payment_blueprint
from app.controllers.categories_controller import category_blueprint
from app.controllers.banner_controller import banner_blueprint
from app.controllers.brand_controller import brand_blueprint
from app.controllers.cart_controller import cart_blueprint
from app.controllers.order_controller import order_blueprint
from app.controllers.user_controller import user_blueprint
from app.controllers.statistics_controller import statistics_blueprint
from app.middlewares.rate_limiter import limit_requests

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, supports_credentials=True, resources={r"/*": {"origins": "http://localhost:3000"}})


    # Initialize database
    init_database(app)

    check_db_connection(app)

    @app.before_request
    def apply_rate_limit():
        response = limit_requests()  
        if response:  
            return response

    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(test_blueprint, url_prefix='/test')  
    app.register_blueprint(user_blueprint, url_prefix='/user')
    app.register_blueprint(product_blueprint, url_prefix='/product')
    app.register_blueprint(payment_blueprint, url_prefix='/payment')
    app.register_blueprint(category_blueprint, url_prefix='/category')
    app.register_blueprint(banner_blueprint, url_prefix='/banners')
    app.register_blueprint(brand_blueprint, url_prefix='/brand')
    app.register_blueprint(cart_blueprint, url_prefix='/cart')
    app.register_blueprint(order_blueprint, url_prefix='/order')
    app.register_blueprint(statistics_blueprint, url_prefix='/statistics')

    return app
