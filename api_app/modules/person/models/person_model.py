from main import db
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from pytz import UTC

class Person(db.Model):
    #__bind_key__ = 'main'
    __tablename__ = "pescod"

    id = db.Column('pescod_id', db.Integer, primary_key=True)
    uid = db.Column(db.String(36), unique=True, nullable=False)
    main_organization_id_fk = db.Column('instit_id_fk', db.Integer, db.ForeignKey('instit.instit_id')) # the uid for the main organization
    main_organization_uid_fk = db.Column(db.String(36), db.ForeignKey('instit.uid')) # the uid for the main organization
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
    phone = relationship("Phone", back_populates="person", lazy='select', foreign_keys="[Phone.person_uid_fk]")
    mail = relationship("Mail", back_populates="person", lazy='select', foreign_keys="[Mail.person_uid_fk]")
    address = relationship("Address", back_populates="person", lazy='select', foreign_keys="[Address.person_uid_fk]")
    person_natural = relationship("PersonNatural", back_populates="person", uselist=False, foreign_keys="[PersonNatural.person_uid_fk]")
    person_legal = relationship("PersonLegal", back_populates="person", uselist=False, foreign_keys="[PersonLegal.person_uid_fk]")
    users = relationship("Users", back_populates="person", lazy='select', foreign_keys="[Users.person_uid_fk]")
    organization = relationship("Organization", back_populates="person", foreign_keys=[main_organization_uid_fk])

    #pronoun = relationship("Pronoun", back_populates="persons", lazy='select')

    def to_dict(self):
        return {
            'id': self.id,
            'uid': self.uid,
            'main_organization_id_fk': self.main_organization_id_fk,
            'main_organization_uid_fk': self.main_organization_uid_fk,
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
            id=data.get("id"),
            uid=data.get("uid"),
            main_organization_id_fk=data.get("main_organization_id_fk"),
            main_organization_uid_fk=data.get("main_organization_uid_fk"),
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