from backend.apps.commerciall_api.main import db
from sqlalchemy import func
from ...utils.parse_json import ParseJson

class Refueling(db.Model):
    __tablename__ = 'vehycle_refueling_order'
    __bind_key__ = 'DB_MAIN'
    
    uid = db.Column(db.String(36), primary_key=True, unique=True)
    organization_uid_fk = db.Column(db.String(36), nullable=False)
    is_active = db.Column(db.Integer, default=0)  # 1 for active, 0 for inactive
    vehycle_uid_fk = db.Column(db.String(36), db.ForeignKey('vehycles.uid'), nullable=False)
    driver_uid_fk = db.Column(db.String(36), db.ForeignKey('vehycle_drivers.uid'), nullable=False)
    order_date = db.Column(db.TIMESTAMP, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    full_tank = db.Column(db.Integer, default=0)  # 1 for full tank, 0 for not full
    fuel_type = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)
    executed_date = db.Column(db.TIMESTAMP, nullable=True)
    attendant_name = db.Column(db.String(100), nullable=True)
    mileage = db.Column(db.Integer, default=0)
    created_at = db.Column(db.TIMESTAMP, default=func.now())
    updated_at = db.Column(db.TIMESTAMP, default=func.now(), onupdate=func.now())

    vehycle = db.relationship('Vehycles', back_populates='refueling_order', lazy=True)
    driver = db.relationship('VehycleDrivers', back_populates='refueling_order', lazy=True)
    
    @staticmethod
    def from_json(json_data):

        return Refueling(
            uid=json_data.get('uid'),
            organization_uid_fk=json_data.get('organization_uid_fk'),
            is_active=ParseJson.true_to_1(json_data.get('is_active')),
            vehycle_uid_fk=json_data.get('vehycle_uid_fk'),
            driver_uid_fk=json_data.get('driver_uid_fk'),
            order_date=json_data.get('order_date'),
            amount=json_data.get('amount'),
            full_tank=ParseJson.true_to_1(json_data.get('full_tank')),
            fuel_type=json_data.get('fuel_type'),
            price=json_data.get('price'),
            executed_date=json_data.get('executed_date'),
            attendant_name=json_data.get('attendant_name'),
            mileage=json_data.get('mileage'),
            created_at=json_data.get('created_at'),
            updated_at=json_data.get('updated_at'),
        )

    def to_dict(self):
        return {
            'uid': self.uid,
            'organization_uid_fk': self.organization_uid_fk,
            'is_active': bool(self.is_active) if self.is_active == 1 else False,
            'vehycle_uid_fk': self.vehycle_uid_fk,
            'driver_uid_fk': self.driver_uid_fk,
            'order_date': self.order_date,
            'amount': self.amount,
            'full_tank': bool(self.full_tank) if self.full_tank == 1 else False,
            'fuel_type': self.fuel_type,
            'price': self.price,
            'executed_date': self.executed_date,
            'attendant_name': self.attendant_name,
            'mileage': self.mileage,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }