from main import db
from datetime import datetime
from sqlalchemy.orm import relationship
from pytz import UTC

class PersonControl(db.Model):
    __bind_key__ = 'main'
    __tablename__ = "pescod"

    id = db.Column('pescod_id', db.Integer, primary_key=True)
    entity_id_fk = db.Column('instit_id_fk', db.Integer, primary_key=False)
    person_type = db.Column('tipo', db.Integer, primary_key=False)
    is_active = db.Column('sit', db.Integer, primary_key=False)
    is_supplier = db.Column('forn', db.Integer, primary_key=False)
    id_number = db.Column('cpfcnpj', db.String, primary_key=False)
    name = db.Column('nomeOrRazaoSocial', db.String, primary_key=False)
    picture = db.Column('foto', db.String, primary_key=False)
    img_bites = db.Column('img_bites', db.Integer, primary_key=False)
    credit = db.Column('limite', db.Numeric, primary_key=False)
    balance = db.Column('saldo', db.Numeric, primary_key=False)
    created_at = db.Column('data_criacao', db.TIMESTAMP(timezone=True), primary_key=False)
    updated_at = db.Column('data_atualizacao', db.TIMESTAMP(timezone=True), primary_key=False)

    phones = relationship("Phones", back_populates="person_control", lazy='select')
    mails = relationship("Mails", back_populates="person_control", lazy='select')
    addresses = relationship("Address", back_populates="person_control", lazy='select')
    person_natural = relationship("PersonNatural", back_populates="person_control", uselist=False)

    def to_dict(self):
        return {
            'id': self.id,
            'entity_id_fk': self.entity_id_fk,
            'person_type': self.person_type,
            'is_active': bool(self.is_active) if self.is_active == 1 else False,
            'is_supplier': bool(self.is_supplier) if self.is_supplier is not None else False,
            'id_number': self.id_number,
            'name': self.name,
            'picture': self.picture,
            'img_bites': self.img_bites,
            'credit': float(self.credit) if self.credit is not None else None,
            'balance': float(self.balance) if self.balance is not None else None,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }