
from datetime import datetime
from pytz import UTC
from main import db
from sqlalchemy.orm import relationship

class AddressType(db.Model):
    __bind_key__ = 'main'  # SQLAlchemy to use the 'main' bind
    __tablename__ = "logradouros"

    id = db.Column('Id', db.Integer, primary_key=True)
    name = db.Column('logr', db.String(20), nullable=True)
    abbreviation = db.Column('abrev', db.String(5), nullable=True)

    addresses = relationship("Addresses", back_populates="address_type", lazy='joined')

    def to_dict(self):
        """Convert model to dictionary using direct attribute access"""
        result = {
            'id': self.id,
            'name': self.name,
            'abbreviation': self.abbreviation
        }
        return result
    
    def __repr__(self):
        return f"<AddressType {self.id} - {self.name}>"