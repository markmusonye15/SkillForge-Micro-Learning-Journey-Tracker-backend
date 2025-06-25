from . import db
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class User(db.Model):
    """
    User model for storing user accounts.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    journeys = relationship('Journey', back_populates='user', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<User {self.username}>'