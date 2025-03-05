from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app import db
from app.models import User, UserRole
from email_validator import validate_email, EmailNotValidError

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Регистрация нового пользователя (респондента)
    """
    data = request.get_json()
    
    # Проверка наличия обязательных полей
    if not all(k in data for k in ('username', 'email', 'password')):
        return jsonify({'message': 'Отсутствуют обязательные поля'}), 400
    
    # Проверка уникальности имени пользователя
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Пользователь с таким именем уже существует'}), 400
    
    # Проверка валидности email
    try:
        validate_email(data['email'])
    except EmailNotValidError:
        return jsonify({'message': 'Некорректный email'}), 400
    
    # Проверка уникальности email
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Пользователь с таким email уже существует'}), 400
    
    # Создание нового пользователя
    user = User(
        username=data['username'],
        email=data['email'],
        password=data['password'],
        role=UserRole.RESPONDENT.value
    )
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify(user.to_dict()), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Вход в систему
    """
    data = request.get_json()
    
    # Проверка наличия обязательных полей
    if not all(k in data for k in ('username', 'password')):
        return jsonify({'message': 'Отсутствуют обязательные поля'}), 400
    
    # Поиск пользователя
    user = User.query.filter_by(username=data['username']).first()
    
    # Проверка пароля
    if not user or not user.check_password(data['password']):
        return jsonify({'message': 'Неверное имя пользователя или пароль'}), 401
    
    # Создание JWT токена
    access_token = create_access_token(identity=user.id)
    
    return jsonify({
        'access_token': access_token,
        'user': user.to_dict()
    }), 200
