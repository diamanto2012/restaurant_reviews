from app import db, create_app
from app.models import User, Restaurant, Review, UserRole

def init_db():
    """
    Инициализация базы данных тестовыми данными
    """
    app = create_app()
    with app.app_context():
        # Создание таблиц
        db.create_all()
        
        # Проверка, есть ли уже данные в базе
        if User.query.count() > 0:
            print("База данных уже содержит данные. Инициализация пропущена.")
            return
        
        # Создание пользователей
        admin = User(
            username="admin",
            email="admin@example.com",
            password="admin123",
            role=UserRole.ADMIN.value
        )
        
        user1 = User(
            username="user1",
            email="user1@example.com",
            password="user123",
            role=UserRole.RESPONDENT.value
        )
        
        user2 = User(
            username="user2",
            email="user2@example.com",
            password="user123",
            role=UserRole.RESPONDENT.value
        )
        
        db.session.add_all([admin, user1, user2])
        db.session.commit()
        
        # Создание ресторанов
        restaurant1 = Restaurant(
            name="Итальянская кухня",
            address="ул. Пушкина, 10",
            description="Ресторан итальянской кухни с уютной атмосферой"
        )
        
        restaurant2 = Restaurant(
            name="Японский сад",
            address="ул. Ленина, 25",
            description="Ресторан японской кухни с аутентичным интерьером"
        )
        
        restaurant3 = Restaurant(
            name="Русские традиции",
            address="ул. Гагарина, 5",
            description="Ресторан русской кухни с традиционными блюдами"
        )
        
        db.session.add_all([restaurant1, restaurant2, restaurant3])
        db.session.commit()
        
        # Создание отзывов
        review1 = Review(
            restaurant_id=restaurant1.id,
            user_id=user1.id,
            food_rating=5,
            drinks_rating=4,
            overall_rating=5,
            comment="Отличная паста и вино!"
        )
        
        review2 = Review(
            restaurant_id=restaurant2.id,
            user_id=user1.id,
            food_rating=4,
            drinks_rating=5,
            overall_rating=4,
            comment="Свежие суши, рекомендую!"
        )
        
        review3 = Review(
            restaurant_id=restaurant1.id,
            user_id=user2.id,
            food_rating=3,
            drinks_rating=4,
            overall_rating=3,
            comment="Неплохая пицца, но долго ждали"
        )
        
        db.session.add_all([review1, review2, review3])
        db.session.commit()
        
        print("База данных успешно инициализирована тестовыми данными.")

if __name__ == "__main__":
    init_db()
