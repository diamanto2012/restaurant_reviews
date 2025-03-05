from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from app import db
from app.models import Review, Restaurant, User
from app.utils.auth import admin_required, user_can_view_review

reviews_bp = Blueprint('reviews', __name__)

@reviews_bp.route('', methods=['GET'])
@jwt_required()
def get_reviews():
    """
    Получение списка отзывов
    Администраторы могут получать все отзывы
    Респонденты могут получать только свои отзывы
    """
    current_user = User.query.get(get_jwt_identity())
    
    # Проверка, что пользователь существует
    if not current_user:
        return jsonify({'message': 'Пользователь не найден'}), 404
    
    # Получение параметров запроса
    restaurant_id = request.args.get('restaurant_id', type=int)
    user_id = request.args.get('user_id', type=int)
    
    # Базовый запрос
    query = Review.query
    
    # Фильтрация по ресторану
    if restaurant_id:
        query = query.filter(Review.restaurant_id == restaurant_id)
    
    # Фильтрация по пользователю
    if user_id:
        # Проверка прав доступа
        if not current_user.is_admin() and user_id != current_user.id:
            return jsonify({'message': 'Доступ запрещен'}), 403
        query = query.filter(Review.user_id == user_id)
    # Если пользователь не администратор и не указан user_id, показываем только его отзывы
    elif not current_user.is_admin():
        query = query.filter(Review.user_id == current_user.id)
    
    reviews = query.all()
    return jsonify([review.to_dict() for review in reviews]), 200

@reviews_bp.route('/<int:review_id>', methods=['GET'])
@jwt_required()
def get_review(review_id):
    """
    Получение данных отзыва
    Администраторы могут получать любой отзыв
    Респонденты могут получать только свои отзывы
    """
    review = Review.query.get(review_id)
    if not review:
        return jsonify({'message': 'Отзыв не найден'}), 404
    
    # Проверка прав доступа
    if not user_can_view_review(review):
        return jsonify({'message': 'Доступ запрещен'}), 403
    
    return jsonify(review.to_dict()), 200

@reviews_bp.route('', methods=['POST'])
@jwt_required()
def create_review():
    """
    Создание нового отзыва (для респондентов)
    """
    data = request.get_json()
    
    # Проверка наличия обязательных полей
    required_fields = ['restaurant_id', 'food_rating', 'drinks_rating', 'overall_rating']
    if not all(k in data for k in required_fields):
        return jsonify({'message': 'Отсутствуют обязательные поля'}), 400
    
    # Проверка валидности оценок
    for rating_field in ['food_rating', 'drinks_rating', 'overall_rating']:
        rating = data.get(rating_field)
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            return jsonify({'message': f'Поле {rating_field} должно быть целым числом от 1 до 5'}), 400
    
    # Получение текущего пользователя
    current_user_id = get_jwt_identity()
    
    # Проверка существования ресторана
    restaurant = Restaurant.query.get(data['restaurant_id'])
    if not restaurant:
        return jsonify({'message': 'Ресторан не найден'}), 404
    
    # Создание нового отзыва
    review = Review(
        restaurant_id=data['restaurant_id'],
        user_id=current_user_id,
        food_rating=data['food_rating'],
        drinks_rating=data['drinks_rating'],
        overall_rating=data['overall_rating'],
        comment=data.get('comment')
    )
    
    try:
        db.session.add(review)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'Вы уже оставили отзыв для этого ресторана'}), 400
    
    return jsonify(review.to_dict()), 201
