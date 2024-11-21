from flask import Flask
from app.configs.database_configs import init_database, check_db_connection
from app.configs.core_configs import Config
from flask_cors import CORS
from app.controllers.auth_controller import auth_blueprint
from app.controllers.test_controller import test_blueprint
from app.controllers.product_controller import product_blueprint
from app.middlewares.rate_limiter import limit_requests

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, supports_credentials=True)

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
    app.register_blueprint(product_blueprint, url_prefix='/product')
    return app
