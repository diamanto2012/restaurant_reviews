from app import db
from datetime import datetime
from sqlalchemy import CheckConstraint, UniqueConstraint

class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    food_rating = db.Column(db.Integer, nullable=False)
    drinks_rating = db.Column(db.Integer, nullable=False)
    overall_rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Отношения
    restaurant = db.relationship('Restaurant', back_populates='reviews')
    user = db.relationship('User', back_populates='reviews')
    
    # Ограничения
    __table_args__ = (
        CheckConstraint('food_rating >= 1 AND food_rating <= 5', name='check_food_rating'),
        CheckConstraint('drinks_rating >= 1 AND drinks_rating <= 5', name='check_drinks_rating'),
        CheckConstraint('overall_rating >= 1 AND overall_rating <= 5', name='check_overall_rating'),
        UniqueConstraint('user_id', 'restaurant_id', name='unique_user_restaurant_review'),
    )
    
    def __init__(self, restaurant_id, user_id, food_rating, drinks_rating, overall_rating, comment=None):
        self.restaurant_id = restaurant_id
        self.user_id = user_id
        self.food_rating = food_rating
        self.drinks_rating = drinks_rating
        self.overall_rating = overall_rating
        self.comment = comment
    
    def to_dict(self):
        return {
            'id': self.id,
            'restaurant_id': self.restaurant_id,
            'user_id': self.user_id,
            'food_rating': self.food_rating,
            'drinks_rating': self.drinks_rating,
            'overall_rating': self.overall_rating,
            'comment': self.comment,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Review {self.id} for Restaurant {self.restaurant_id} by User {self.user_id}>'
