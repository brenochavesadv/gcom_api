from main import db
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from pytz import UTC

class Person(db.Model):
    #__bind_key__ = 'main'
    __tablename__ = "pescod"

    person_id = db.Column('pescod_id', db.Integer, primary_key=True)
    person_uid = db.Column('pescod_uid', db.String(36), unique=True, nullable=False)
    organization_uid_fk = db.Column('instit_id_fk', db.Integer, db.ForeignKey('instit.instit_id')) # the uid for the main organization
    person_type = db.Column('tipo', db.Integer)
    is_active = db.Column('sit', db.Integer)
    is_supplier = db.Column('forn', db.Integer)
    id_number = db.Column('cpfcnpj', db.String(25)) # cpf , cnpj
    name = db.Column('nomeOrRazaoSocial', db.String(100))
    picture = db.Column('foto', db.String(100))
    img_bites = db.Column('img_bites', db.Integer)
    credit = db.Column('limite', db.Numeric(10, 2))
    balance = db.Column('saldo', db.Numeric(10, 2))
    created_at = db.Column('data_criacao', db.TIMESTAMP(timezone=True))
    updated_at = db.Column('data_atualizacao', db.TIMESTAMP(timezone=True))

    phone = relationship("Phone", back_populates="person", lazy='select')
    mail = relationship("Mail", back_populates="person", lazy='select')
    address = relationship("Address", back_populates="person", lazy='select')
    person_natural = relationship("PersonNatural", back_populates="person", uselist=False)
    person_legal = relationship("PersonLegal", back_populates="person", uselist=False)
    #pronoun = relationship("Pronoun", back_populates="persons", lazy='select')

    def to_dict(self):
        return {
            'person_id': self.person_id,
            'person_uid': self.person_uid,
            'organization_uid_fk': self.organization_uid_fk,
            'person_type': self.person_type,
            'is_active': bool(self.is_active) if self.is_active == 1 else False,
            'is_supplier': bool(self.is_supplier) if self.is_supplier is not None else False,
            'id_number': self.id_number,
            'name': self.name,
            'picture': self.picture if self.picture is not None else "nofoto.gif",
            'img_bites': self.img_bites if self.img_bites is not None else 0,
            'credit': float(self.credit) if self.credit is not None else 0,
            'balance': float(self.balance) if self.balance is not None else 0,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    # CREATES A FACTORY FOR PERSON_MODEL:
    @staticmethod
    def person_data(data):
        person = Person(
            person_id=data.get("person_id"),
            person_uid=data.get("person_uid"),
            organization_uid_fk=data.get("organization_uid_fk"),
            person_type=data.get("person_type"),
            is_active=data.get("is_active"),
            is_supplier=data.get("is_supplier"),
            id_number=data.get("id_number"),
            name=data.get("name"),
            picture=data.get("picture"),
            img_bites=8878,  # default value
            credit=data.get("credit"),
            balance=data.get("balance"),
        )
        return person