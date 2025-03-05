import csv
import io
from sqlalchemy import func
from app import db
from app.models import Restaurant, Review

def generate_restaurants_report():
    """
    Генерирует CSV отчет со средними оценками по всем ресторанам
    """
    # Получаем средние оценки для каждого ресторана
    report_data = db.session.query(
        Restaurant.id,
        Restaurant.name,
        func.avg(Review.food_rating).label('avg_food_rating'),
        func.avg(Review.drinks_rating).label('avg_drinks_rating'),
        func.avg(Review.overall_rating).label('avg_overall_rating'),
        func.count(Review.id).label('reviews_count')
    ).outerjoin(Review).group_by(Restaurant.id).all()
    
    # Создаем CSV файл в памяти
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Записываем заголовки
    writer.writerow([
        'ID ресторана', 
        'Название ресторана', 
        'Средняя оценка еды', 
        'Средняя оценка напитков', 
        'Средняя общая оценка', 
        'Количество отзывов'
    ])
    
    # Записываем данные
    for row in report_data:
        writer.writerow([
            row.id,
            row.name,
            round(row.avg_food_rating, 2) if row.avg_food_rating else 'Нет данных',
            round(row.avg_drinks_rating, 2) if row.avg_drinks_rating else 'Нет данных',
            round(row.avg_overall_rating, 2) if row.avg_overall_rating else 'Нет данных',
            row.reviews_count
        ])
    
    # Получаем содержимое CSV файла
    output.seek(0)
    return output.getvalue()
