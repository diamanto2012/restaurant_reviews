from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required
from app import db
from app.models import Restaurant
from app.utils.auth import admin_required
from app.utils.report_generator import generate_restaurants_report

restaurants_bp = Blueprint('restaurants', __name__)

@restaurants_bp.route('', methods=['GET'])
def get_restaurants():
    """
    Получение списка всех ресторанов (доступно всем)
    """
    restaurants = Restaurant.query.all()
    return jsonify([restaurant.to_dict() for restaurant in restaurants]), 200

@restaurants_bp.route('/<int:restaurant_id>', methods=['GET'])
def get_restaurant(restaurant_id):
    """
    Получение данных ресторана (доступно всем)
    """
    restaurant = Restaurant.query.get(restaurant_id)
    if not restaurant:
        return jsonify({'message': 'Ресторан не найден'}), 404
    
    return jsonify(restaurant.to_dict()), 200

@restaurants_bp.route('', methods=['POST'])
@admin_required()
def create_restaurant():
    """
    Создание нового ресторана (только для администраторов)
    """
    data = request.get_json()
    
    # Проверка наличия обязательных полей
    if 'name' not in data:
        return jsonify({'message': 'Отсутствует обязательное поле "name"'}), 400
    
    # Создание нового ресторана
    restaurant = Restaurant(
        name=data['name'],
        address=data.get('address'),
        description=data.get('description')
    )
    
    db.session.add(restaurant)
    db.session.commit()
    
    return jsonify(restaurant.to_dict()), 201

@restaurants_bp.route('/<int:restaurant_id>', methods=['PUT'])
@admin_required()
def update_restaurant(restaurant_id):
    """
    Обновление данных ресторана (только для администраторов)
    """
    restaurant = Restaurant.query.get(restaurant_id)
    if not restaurant:
        return jsonify({'message': 'Ресторан не найден'}), 404
    
    data = request.get_json()
    
    # Обновление названия
    if 'name' in data:
        restaurant.name = data['name']
    
    # Обновление адреса
    if 'address' in data:
        restaurant.address = data['address']
    
    # Обновление описания
    if 'description' in data:
        restaurant.description = data['description']
    
    db.session.commit()
    
    return jsonify(restaurant.to_dict()), 200

@restaurants_bp.route('/<int:restaurant_id>', methods=['DELETE'])
@admin_required()
def delete_restaurant(restaurant_id):
    """
    Удаление ресторана (только для администраторов)
    """
    restaurant = Restaurant.query.get(restaurant_id)
    if not restaurant:
        return jsonify({'message': 'Ресторан не найден'}), 404
    
    db.session.delete(restaurant)
    db.session.commit()
    
    return '', 204

@restaurants_bp.route('/report', methods=['GET'])
@admin_required()
def get_restaurants_report():
    """
    Выгрузка сводного отчета по всем ресторанам (только для администраторов)
    """
    csv_data = generate_restaurants_report()
    
    # Создание ответа с CSV файлом
    response = Response(csv_data, mimetype='text/csv')
    response.headers.set('Content-Disposition', 'attachment', filename='restaurants_report.csv')
    
    return response
