from datetime import datetime
from pytz import UTC
from main import db
from sqlalchemy.orm import relationship

class AddressUnit(db.Model):
    #__bind_key__ = 'main'  # SQLAlchemy to use the 'main' bind
    __tablename__ = "address_unit"

    uid = db.Column(db.String(10), nullable=True, primary_key=True, comment='based on US Postal Service Standard abbreviation')
    description_en_us = db.Column(db.String(20))
    abbrev_en_us = db.Column(db.String(10), comment='abbreviation based on US Postal Service Standard abbreviation')
    pt_br = db.Column(db.String(20), nullable=True, comment='Portuguese (Brazil) full name')
    abbrev_pt_br = db.Column(db.String(10), nullable=True, comment='Portuguese (Brazil) abbreviation')
    
    def to_dict(self):
        print("Convert model to dictionary using direct attribute access")
        result = {
            'uid': self.uid,
            'description_en_us': self.description_en_us,
            'abbrev_en_us': self.abbrev_en_us,
            'pt_br': self.pt_br,
            'abbrev_pt_br': self.abbrev_pt_br
        }
        return result