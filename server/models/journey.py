from . import db
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Journey(db.Model):
    """
    Journey model for storing learning journeys.
    """
    __tablename__ = 'journeys'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    
   
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = relationship('User', back_populates='journeys')
    steps = relationship('Step', back_populates='journey', cascade="all, delete-orphan", lazy='dynamic')

    def __repr__(self):
        return f'<Journey {self.title}>'