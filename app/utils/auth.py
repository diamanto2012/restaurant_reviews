from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models import User, UserRole

def admin_required():
    """
    Декоратор для проверки, что пользователь является администратором
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user or user.role != UserRole.ADMIN.value:
                return jsonify({"message": "Доступ запрещен. Требуются права администратора."}), 403
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper

def get_current_user():
    """
    Получение текущего пользователя из JWT токена
    """
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        return User.query.get(user_id)
    except:
        return None

def user_can_view_user(user_id):
    """
    Проверка, может ли текущий пользователь просматривать информацию о пользователе с указанным ID
    """
    current_user = get_current_user()
    
    if not current_user:
        return False
    
    # Администратор может просматривать информацию о любом пользователе
    if current_user.is_admin():
        return True
    
    # Респондент может просматривать только свою информацию
    return current_user.id == user_id

def user_can_view_review(review):
    """
    Проверка, может ли текущий пользователь просматривать отзыв
    """
    current_user = get_current_user()
    
    if not current_user:
        return False
    
    # Администратор может просматривать любой отзыв
    if current_user.is_admin():
        return True
    
    # Респондент может просматривать только свои отзывы
    return current_user.id == review.user_id
