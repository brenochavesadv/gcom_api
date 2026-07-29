from main import db
from sqlalchemy.orm import relationship
from flask import current_app
from ...utils.parse_json import ParseJson

class Person(db.Model):
    __bind_key__ = 'DB_MAIN' 
    __tablename__ = "pescod"

    uid = db.Column('pescod_id', db.Integer, primary_key=True)
    main_organization_uid_fk = db.Column('instit_id_fk', db.Integer, db.ForeignKey('instit.instit_id')) # the uid for the main organization
    person_type = db.Column('tipo', db.Integer)
    is_active = db.Column('sit', db.Integer, comment="2 for active")
    is_supplier = db.Column('forn', db.Integer)
    id_number = db.Column('cpfcnpj', db.String(25)) # cpf , cnpj
    iso2alpha = db.Column(db.String(2))
    name = db.Column('nomeOrRazaoSocial', db.String(100))
    picture = db.Column('foto', db.String(100))
    img_bites = db.Column('img_bites', db.Integer)
    credit_limit = db.Column('limite', db.Numeric(10, 2))
    credit_balance = db.Column('saldo', db.Numeric(10, 2))
    is_credit_available = db.Column(db.SmallInteger, default=0)  # 0 = not available, 1 = available
    block_exceeding_limit = db.Column(db.SmallInteger, default=1)  # 0 = not blocked, 1 = blocked
    created_at = db.Column('data_criacao', db.TIMESTAMP(timezone=True))
    updated_at = db.Column('data_atualizacao', db.TIMESTAMP(timezone=True))
    
    phone = relationship("Phone", back_populates="person", lazy='select', foreign_keys="[Phone.person_uid_fk]")
    mail = relationship("Mail", back_populates="person", lazy='select', foreign_keys="[Mail.person_uid_fk]")
    address = relationship("Address", back_populates="person", lazy='select', foreign_keys="[Address.person_uid_fk]")
    person_natural = relationship("PersonNatural", back_populates="person", uselist=False, foreign_keys="[PersonNatural.person_uid_fk]")
    person_legal = relationship("PersonLegal", back_populates="person", uselist=False, foreign_keys="[PersonLegal.person_uid_fk]")
    person_legal_br_tax_regime = relationship("PersonLegalBrTaxRegime", back_populates="person", lazy='select', foreign_keys="[PersonLegalBrTaxRegime.person_uid_fk]")
    person_legal_activity = relationship("PersonLegalActivity", back_populates="person", lazy='select', foreign_keys="[PersonLegalActivity.person_uid_fk]")
    person_legal_partner = relationship("PersonLegalPartner", back_populates="person", lazy='select', foreign_keys="[PersonLegalPartner.person_uid_fk]")
    user_organizations = relationship("UserOrganizations", back_populates="person", lazy='select', foreign_keys="[UserOrganizations.person_uid_fk]")
    organization = relationship("Organization", back_populates="person", foreign_keys=[main_organization_uid_fk])
    vehycle_drivers = relationship("VehycleDrivers", back_populates="person", lazy='select', foreign_keys="[VehycleDrivers.person_uid_fk]")
    
    #pronoun = relationship("Pronoun", back_populates="persons", lazy='select')

    def to_dict(self):
        return {
            'uid': self.uid,
            'main_organization_uid_fk': self.main_organization_uid_fk,
            'person_type': self.person_type,
            'is_active': bool(self.is_active) if self.is_active == 2 else False,
            'is_supplier': bool(self.is_supplier) if self.is_supplier == 1 else False,
            'id_number': self.id_number,
            'iso2alpha': self.iso2alpha if self.iso2alpha is not None else "",
            'name': self.name,
            'picture': self.picture if self.picture is not None else "nofoto.gif",
            'img_bites': self.img_bites if self.img_bites is not None else 0,
            'credit_limit': float(self.credit_limit) if self.credit_limit is not None else 0,
            'credit_balance': float(self.credit_balance) if self.credit_balance is not None else 0,
            'is_credit_available': bool(self.is_credit_available) if self.is_credit_available == 1 else False,
            'block_exceeding_limit': bool(self.block_exceeding_limit) if self.block_exceeding_limit == 1 else False,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    # CREATES A FACTORY FOR PERSON_MODEL:
    @staticmethod
    def from_json(data):
        current_app.logger.debug(f"Received person data: {data}")

        person = Person(    
            uid=int(data.get("uid")) if data.get("uid") is not None else None,
            main_organization_uid_fk=int(data.get("main_organization_uid_fk")) if data.get("main_organization_uid_fk") is not None else None,
            person_type=data.get("person_type"),
            is_active=ParseJson.return_int_for_true(data.get("is_active"), 2),  # 2 for active, 1 for inactive
            is_supplier=ParseJson.return_int_for_true(data.get("is_supplier"), 1),  # 1 for supplier, 0 for not supplier
            id_number=data.get("id_number"),
            iso2alpha=data.get("iso2alpha"),
            name=data.get("name"),
            picture=data.get("picture"),
            img_bites=8878,  # default value
            credit_limit=data.get("credit_limit"),
            credit_balance=data.get("credit_balance"),
            is_credit_available=data.get("is_credit_available"),
            block_exceeding_limit=int(data.get("block_exceeding_limit")) if data.get("block_exceeding_limit") is not None else 1,  # default to 1 (blocked) if not provided
        )
        return person