from datetime import datetime
from pytz import UTC
from main import db
from sqlalchemy.orm import relationship

class AddressSuffix(db.Model):
    __bind_key__ = 'DB_MAIN' 
    __tablename__ = "address_suffix"

    uid = db.Column(db.String(10), nullable=True, primary_key=True, comment='based on US Postal Service Standard abbreviation')
    suffix = db.Column(db.String(25), primary_key=True)
    common_abbrev_en_us = db.Column(db.String(100), nullable=True, comment='list of Common abbreviations in English')
    en_us = db.Column(db.String(20), nullable=True, comment='English (United States) full name')
    pt_br = db.Column(db.String(20), nullable=True, comment='Portuguese (Brazil) full name')
    abbrev_pt_br = db.Column(db.String(10), nullable=True, comment='Portuguese (Brazil) abbreviation')
   
    def to_dict(self):
        """Convert model to dictionary using direct attribute access"""
        result = {
            'uid': self.uid,
            'suffix': self.suffix,
            'common_abbrev_en_us': self.common_abbrev_en_us if self.common_abbrev_en_us is not None else "",
            'en_us': self.en_us if self.en_us is not None else "",
            'pt_br': self.pt_br if self.pt_br is not None else "",
            'abbrev_pt_br': self.abbrev_pt_br if self.abbrev_pt_br is not None else "",
        }
        return result