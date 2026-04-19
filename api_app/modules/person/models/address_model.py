from datetime import datetime
from celery import uuid
from pytz import UTC
from api_app.modules.person.models.person_model import Person
from main import db
from sqlalchemy.orm import relationship

class Address(db.Model):
    __bind_key__ = 'DB_MAIN' 
    __tablename__ = "enderecos"

    id = db.Column('enderecos_id', db.Integer, primary_key=True)
    uid = db.Column(db.String(36), unique=True, nullable=False)  # UUID for external reference
    is_active = db.Column(db.SmallInteger, nullable=False, default=0, comment='1:active 0:not')
    is_main = db.Column(db.SmallInteger, nullable=False, default=0, comment='1:main address 0:not')
    person_id_fk = db.Column('pescod_id_fk', db.Integer, db.ForeignKey('pescod.pescod_id'))
    person_uid_fk = db.Column(db.String(36), db.ForeignKey('pescod.uid'))
    address_label = db.Column(db.String(20), nullable=True, comment='Label for the address, e.g., "Home", "Office"')
    suffix = db.Column('logradouros_id_fk', db.String(10), nullable=False, comment='Street, Avenue, etc. suffix identifier')
    address = db.Column('logradouro', db.String(100), nullable=True)
    number = db.Column('numero', db.String(8), nullable=True)
    complement = db.Column('complemento', db.String(50), nullable=True)
    nbhd = db.Column('bairro', db.String(40), nullable=True)
    zip_code = db.Column('cep', db.String(10), nullable=True)
    city_code = db.Column('municipios_id_fk', db.Integer, nullable=True)
    city_name = db.Column(db.String(60), nullable=True, comment='City name')
    state_abbrev = db.Column(db.String(5), nullable=True, comment='State abbreviation')
    state_name = db.Column(db.String(50), nullable=True, comment='State name')
    iso2alpha = db.Column(db.String(3), nullable=True, comment='Country ISO 2 Alpha code')
    created_at = db.Column('data_criacao', db.TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=True)
    updated_at = db.Column('data_atualizacao', db.TIMESTAMP(timezone=True), nullable=True)

    person = relationship("Person", back_populates="address", foreign_keys=[person_id_fk])

    def to_dict(self):
        """Convert model to dictionary using direct attribute access"""
        result = {
            'id': self.id,
            'uid': self.uid,
            'is_active': bool(self.is_active) if self.is_active == 1 else False,
            'is_main': self.is_main,
            'person_id_fk': self.person_id_fk,
            'person_uid_fk': self.person_uid_fk,
            'address_label': self.address_label if self.address_label is not None else "",
            'suffix': self.suffix,
            'address': self.address if self.address is not None else "",
            'number': self.number if self.number is not None else "",
            'complement': self.complement if self.complement is not None else "",
            'nbhd': self.nbhd if self.nbhd is not None else "",
            'zip_code': self.zip_code if self.zip_code is not None else "",
            'city_code': self.city_code,
            'city_name': self.city_name if self.city_name is not None else "",
            'state_abbrev': self.state_abbrev if self.state_abbrev is not None else "",
            'state_name': self.state_name if self.state_name is not None else "",
            'iso2alpha': self.iso2alpha if self.iso2alpha is not None else "",
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }
        return result
    
    # CREATES A FACTORY FOR ADDRESS_MODEL:
    @staticmethod
    def address_data(data,is_create=False):
        # Don't pass address uid for new records - let database auto-generate it
        
        address = Address(
            id=data.get("id"),
            uid=data.get("uid"),
            is_active=data.get("is_active"),
            is_main=data.get("is_main"),
            person_id_fk=data.get("person_id_fk"),
            person_uid_fk=data.get("person_uid_fk"),
            address_label=data.get("address_label"),
            suffix=data.get("suffix"),
            address=data.get("address"),
            number=data.get("number"),
            complement=data.get("complement"),
            nbhd=data.get("nbhd"),
            zip_code=data.get("zip_code"),
            city_code=data.get("city_code"),
            city_name=data.get("city_name"),
            state_abbrev=data.get("state_abbrev"),
            state_name=data.get("state_name"),
            iso2alpha=data.get("country_iso2alpha"),
        )
        if is_create:
            address.created_at = datetime.now()
        return address

    def __repr__(self):
        return f"<Address {self.uid} - {self.address}>"