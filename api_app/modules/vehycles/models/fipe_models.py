from sqlalchemy import func
from sqlalchemy.orm import relationship
from main import db
import uuid

# Modelos Python/Flask
from main import db

class FipeSyncControl(db.Model):
    __tablename__ = 'fipe_sync_control'
    __bind_key__ = 'DB_FROTALL'

    uid = db.Column(db.String(36), primary_key=True, unique=True)
    type = db.Column(db.String(10), nullable=False)
    brands_last_update_at = db.Column(db.TIMESTAMP, nullable=True)
    vehycle_brand = db.Column(db.Integer, nullable=True)
    vehycle_brand_last_update_at = db.Column(db.TIMESTAMP, nullable=True)

class FipeBrand(db.Model):
    __tablename__ = 'fipe_brand'
    __bind_key__ = 'DB_FROTALL'

    uid = db.Column(db.String(36), primary_key=True, unique=True)
    fipe_code = db.Column(db.String(6), nullable=True)
    name = db.Column(db.String(128), nullable=True)
    type = db.Column(db.String(12), nullable=False)    
    
    def to_dict(self):
        return {
            'uid': self.uid,
            'fipe_code': self.fipe_code,
            'name': self.name,
            'type': self.type if self.type else None,
        }

    @staticmethod
    def from_json(json_data):
        return FipeBrand(
            uid=json_data.get('uid'),
            fipe_code=json_data.get('fipe_code'),
            name=json_data.get('name'),
            type=json_data.get('type'),
        )

class FipeVehycle(db.Model):
    __tablename__ = 'fipe_vehycle'
    __bind_key__ = 'DB_FROTALL'

    uid = db.Column(db.String(36), primary_key=True, unique=True)
    fipe_code = db.Column(db.String(10), nullable=True)
    name = db.Column(db.String(128), nullable=True)
    model_years = db.Column(db.String(255), nullable=True)
    fipe_brand_code_fk = db.Column(db.String(6), db.ForeignKey('fipe_brand.fipe_code'))
    type = db.Column(db.String(10), nullable=False)

    brand = db.relationship('FipeBrand', backref=db.backref('fipe_vehycle', lazy=True))

    def to_dict(self):
        return {
            'uid': self.uid,
            'fipe_code': self.fipe_code,
            'name': self.name,
            'model_years': self.model_years,
            'fipe_brand_code_fk': self.fipe_brand_code_fk,
            'type': self.type,
        }
        
