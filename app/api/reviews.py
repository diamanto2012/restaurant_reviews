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
    current_user = User.query.get(int(get_jwt_identity()))
    
    if not current_user:
        return jsonify({'message': 'Пользователь не найден'}), 404
    
    if current_user.is_admin():
        reviews = Review.query.all()
    else:
        reviews = Review.query.filter_by(user_id=current_user.id).all()
    
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
    
    if not all(k in data for k in ('restaurant_id', 'food_rating', 'drinks_rating', 'overall_rating')):
        return jsonify({'message': 'Отсутствуют обязательные поля'}), 400
    
    # Проверка валидности оценок
    for rating_field in ['food_rating', 'drinks_rating', 'overall_rating']:
        rating = data.get(rating_field)
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            return jsonify({'message': f'Поле {rating_field} должно быть целым числом от 1 до 5'}), 400
    
    restaurant = Restaurant.query.get(data['restaurant_id'])
    if not restaurant:
        return jsonify({'message': 'Ресторан не найден'}), 404
    
    current_user = User.query.get(int(get_jwt_identity()))
    
    if not current_user:
        return jsonify({'message': 'Пользователь не найден'}), 404
    
    review = Review(
        restaurant_id=data['restaurant_id'],
        user_id=current_user.id,
        food_rating=data['food_rating'],
        drinks_rating=data['drinks_rating'],
        overall_rating=data['overall_rating'],
        comment=data.get('comment', '')
    )
    
    try:
        db.session.add(review)
        db.session.commit()
        return jsonify(review.to_dict()), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'Вы уже оставили отзыв для этого ресторана'}), 400
