from sqlalchemy import func
from sqlalchemy.orm import relationship
from api_app.modules.vehycles.models.fipe_models import FipeBrand
from main import db

# Enum para tipos de veículos
from enum import Enum

class VehyclesTypes(Enum):
  cars = 'cars'
  motorcycles = 'motorcycles'
  trucks = 'trucks'

# Modelos Python/Flask
from main import db

class Vehycles(db.Model):
    __tablename__ = 'vehycles'
    __bind_key__ = 'DB_FROTALL'
    
    uid = db.Column(db.String(36), primary_key=True, unique=True)
    organization_uid_fk = db.Column(db.String(36), nullable=False)
    is_active = db.Column(db.Integer, default=0)  # 1 for active, 0 for inactive
    fipe_code = db.Column(db.String(10), nullable=True)
    name = db.Column(db.String(128), nullable=True)
    nickname = db.Column(db.String(30), nullable=True)
    plate = db.Column(db.String(12), nullable=True)
    fipe_brand_code = db.Column(db.String(8), db.ForeignKey('fipe_brand.fipe_code'), nullable=True)
    type = db.Column(db.String(12), nullable=False)
    year = db.Column(db.String(8), nullable=True)
    acquisition_value = db.Column(db.Float, nullable=True)
    acquisition_date = db.Column(db.TIMESTAMP)
    created_at = db.Column(db.TIMESTAMP, default=func.now())
    updated_at = db.Column(db.TIMESTAMP, default=func.now(), onupdate=func.now())

    brand = db.relationship('FipeBrand', backref=db.backref('vehycles', lazy=True))
            
    @staticmethod
    def from_json(json_data):

        return Vehycles(
            uid=json_data.get('uid'),
            organization_uid_fk=json_data.get('organization_uid_fk'),
            is_active=json_data.get('is_active', 0),
            fipe_code=json_data.get('fipe_code'),
            name=json_data.get('name'),
            nickname=json_data.get('nickname'),
            plate=json_data.get('plate'),
            fipe_brand_code=json_data.get('fipe_brand_code'),
            type=json_data.get('type'),
            year=json_data.get('year'),
            acquisition_value=json_data.get('acquisition_value'),
            acquisition_date=json_data.get('acquisition_date'),
            created_at=json_data.get('created_at'),
            updated_at=json_data.get('updated_at'),
        )

    def to_dict(self):
        return {
            'uid': self.uid,
            'organization_uid_fk': self.organization_uid_fk,
            'is_active': bool(self.is_active) if self.is_active == 1 else False,
            'fipe_code': self.fipe_code,
            'name': self.name,
            'nickname': self.nickname,
            'plate': self.plate,
            'fipe_brand_code': self.fipe_brand_code,
            'type': self.type,
            'year': self.year,
            'acquisition_value': self.acquisition_value,
            'acquisition_date': self.acquisition_date,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'brand': self.brand.to_dict() if self.brand else None,
        }
