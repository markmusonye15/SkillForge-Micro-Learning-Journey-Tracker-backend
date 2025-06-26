from . import db
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Step(db.Model):
    """
    Step model for storing individual steps or tasks within a journey.
    """
    __tablename__ = 'steps'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_complete = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())


    journey_id = db.Column(db.Integer, db.ForeignKey('journeys.id'), nullable=False)
    journey = relationship('Journey', back_populates='steps')

    def __repr__(self):
        return f'<Step {self.title}>'