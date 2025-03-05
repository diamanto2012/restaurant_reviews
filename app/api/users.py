from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, UserRole
from app.utils.auth import admin_required, user_can_view_user
from email_validator import validate_email, EmailNotValidError

users_bp = Blueprint('users', __name__)

@users_bp.route('', methods=['GET'])
@admin_required()
def get_users():
    """
    Получение списка всех пользователей (только для администраторов)
    """
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200

@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """
    Получение данных пользователя
    Администраторы могут получать данные любого пользователя
    Респонденты могут получать только свои данные
    """
    # Проверка прав доступа
    if not user_can_view_user(user_id):
        return jsonify({'message': 'Доступ запрещен'}), 403
    
    # Поиск пользователя
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'Пользователь не найден'}), 404
    
    return jsonify(user.to_dict()), 200

@users_bp.route('', methods=['POST'])
@admin_required()
def create_user():
    """
    Создание нового пользователя (только для администраторов)
    """
    data = request.get_json()
    
    # Проверка наличия обязательных полей
    if not all(k in data for k in ('username', 'email', 'password', 'role')):
        return jsonify({'message': 'Отсутствуют обязательные поля'}), 400
    
    # Проверка роли
    if data['role'] not in [UserRole.ADMIN.value, UserRole.RESPONDENT.value]:
        return jsonify({'message': 'Некорректная роль'}), 400
    
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
        role=data['role']
    )
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify(user.to_dict()), 201

@users_bp.route('/<int:user_id>', methods=['PUT'])
@admin_required()
def update_user(user_id):
    """
    Обновление данных пользователя (только для администраторов)
    """
    # Поиск пользователя
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'Пользователь не найден'}), 404
    
    data = request.get_json()
    
    # Обновление имени пользователя
    if 'username' in data:
        # Проверка уникальности имени пользователя
        existing_user = User.query.filter_by(username=data['username']).first()
        if existing_user and existing_user.id != user_id:
            return jsonify({'message': 'Пользователь с таким именем уже существует'}), 400
        user.username = data['username']
    
    # Обновление email
    if 'email' in data:
        # Проверка валидности email
        try:
            validate_email(data['email'])
        except EmailNotValidError:
            return jsonify({'message': 'Некорректный email'}), 400
        
        # Проверка уникальности email
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user and existing_user.id != user_id:
            return jsonify({'message': 'Пользователь с таким email уже существует'}), 400
        user.email = data['email']
    
    # Обновление пароля
    if 'password' in data:
        user.set_password(data['password'])
    
    # Обновление роли
    if 'role' in data:
        if data['role'] not in [UserRole.ADMIN.value, UserRole.RESPONDENT.value]:
            return jsonify({'message': 'Некорректная роль'}), 400
        user.role = data['role']
    
    db.session.commit()
    
    return jsonify(user.to_dict()), 200

@users_bp.route('/<int:user_id>', methods=['DELETE'])
@admin_required()
def delete_user(user_id):
    """
    Удаление пользователя (только для администраторов)
    """
    # Поиск пользователя
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'Пользователь не найден'}), 404
    
    # Проверка, что пользователь не удаляет сам себя
    current_user_id = get_jwt_identity()
    if user_id == current_user_id:
        return jsonify({'message': 'Невозможно удалить текущего пользователя'}), 400
    
    db.session.delete(user)
    db.session.commit()
    
    return '', 204
