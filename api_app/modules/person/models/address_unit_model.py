from datetime import datetime
from pytz import UTC
from main import db
from sqlalchemy.orm import relationship

class AddressUnit(db.Model):
    __bind_key__ = 'DB_MAIN' 
    __tablename__ = "address_unit"

    uid = db.Column(db.Integer, nullable=False, primary_key=True)
    iso2alpha = db.Column(db.String(2), nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    abbrev = db.Column(db.String(10), nullable=False)
    
   
    def to_dict(self):
        """Convert model to dictionary using direct attribute access"""
        result = {
            'uid': self.uid,
            'iso2alpha': self.iso2alpha,
            'suffix': self.unit,
            'abbrev': self.abbrev,
        }
        return result