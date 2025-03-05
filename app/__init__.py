import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_swagger_ui import get_swaggerui_blueprint
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

# Инициализация расширений
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_class=None):
    app = Flask(__name__)
    
    # Конфигурация приложения
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///restaurant_reviews.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'default-jwt-secret-key')
    
    # Инициализация расширений с приложением
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # Регистрация Swagger UI
    SWAGGER_URL = '/api/docs'
    API_URL = '/static/swagger.json'
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "Restaurant Reviews API"
        }
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    
    # Импорт и регистрация маршрутов
    from app.api.auth import auth_bp
    from app.api.users import users_bp
    from app.api.restaurants import restaurants_bp
    from app.api.reviews import reviews_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(users_bp, url_prefix='/api/v1/users')
    app.register_blueprint(restaurants_bp, url_prefix='/api/v1/restaurants')
    app.register_blueprint(reviews_bp, url_prefix='/api/v1/reviews')
    
    # Создание директории для статических файлов, если она не существует
    os.makedirs(os.path.join(app.root_path, 'static'), exist_ok=True)
    
    # Создание Swagger спецификации
    from app.utils.swagger import generate_swagger_spec
    with app.app_context():
        generate_swagger_spec(app)
    
    return app
