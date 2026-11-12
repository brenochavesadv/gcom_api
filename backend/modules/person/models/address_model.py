from datetime import datetime
from backend.apps.commerciall_api.main import db
from sqlalchemy.orm import relationship

from backend.modules.utils.parse_json import ParseJson

class Address(db.Model):
    __bind_key__ = 'DB_MAIN' 
    __tablename__ = "enderecos"

    uid = db.Column('enderecos_id', db.Integer, primary_key=True)
    is_active = db.Column('situacao',db.SmallInteger, nullable=False, default=0, comment='1:active 0:not')
    is_main = db.Column(db.SmallInteger, nullable=False, default=0, comment='1:main address 0:not')
    person_uid_fk = db.Column('pescod_id_fk', db.Integer, db.ForeignKey('pescod.pescod_id'))
    address_label = db.Column(db.String(20), nullable=True, comment='Label for the address, e.g., "Home", "Office"')
    suffix = db.Column('logradouros_id_fk', db.String(10), nullable=False, comment='Street, Avenue, etc. suffix identifier')
    address = db.Column('logradouro', db.String(100), nullable=True)
    number = db.Column('numero', db.String(8), nullable=True)
    complement = db.Column('complemento', db.String(50), nullable=True)
    nbhd = db.Column('bairro', db.String(40), nullable=True)
    zip_code = db.Column('cep', db.String(10), nullable=True)
    city_code = db.Column('municipios_id_fk', db.Integer, nullable=True)  # IBGE code if Brazil
    city_name = db.Column(db.String(60), nullable=True, comment='City name')
    state_abbrev = db.Column(db.String(5), nullable=True, comment='State abbreviation')
    state_name = db.Column(db.String(50), nullable=True, comment='State name')
    iso2alpha = db.Column(db.String(3), nullable=True, comment='Country ISO 2 Alpha code')
    sync_status = db.Column(db.String(10), nullable=False, default='PENDING')
    created_at = db.Column('data_criacao', db.TIMESTAMP(timezone=True), default=db.func.now(), nullable=True)
    updated_at = db.Column('data_atualizacao', db.TIMESTAMP(timezone=True), default=db.func.now(), nullable=True)

    person = relationship("Person", back_populates="addresses", foreign_keys=[person_uid_fk])

    def to_dict(self):
        """Convert model to dictionary using direct attribute access"""
        result = {
            'uid': self.uid,
            'is_active': ParseJson.return_int_for_true(self.is_active, 1),
            'is_main': ParseJson.return_int_for_true(self.is_main, 1),
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
            'sync_status': self.sync_status,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }
        return result
    
    # CREATES A FACTORY FOR ADDRESS_MODEL:
    @staticmethod
    def from_json(data):
        """Create an Address instance from a JSON-like dictionary"""

        address = Address(
            uid=int(data.get("uid")) if data.get("uid") else None,  # Normalize empty string to None for PK
            is_active=1 if data.get("is_active") else 0,
            is_main=1 if data.get("is_main") else 0,
            person_uid_fk=int(data.get("person_uid_fk")) if data.get("person_uid_fk") else None,  # Normalize empty string to None for FK
            address_label=data.get("address_label"),
            suffix=data.get("suffix"),
            address=data.get("address"),
            number=data.get("number"),
            complement=data.get("complement"),
            nbhd=data.get("nbhd"),
            zip_code=data.get("zip_code"),
            city_code=int(data.get("city_code")) if data.get("city_code") else None,  # Normalize empty string to None for city_code
            city_name=data.get("city_name"),
            state_abbrev=data.get("state_abbrev"),
            state_name=data.get("state_name") if data.get("state_name") else data.get("state_abbrev"),  # Fallback to state_abbrev if state_name is not provided
            iso2alpha=data.get("iso2alpha"),
            sync_status=data.get("sync_status", "PENDING"),
        )

        return address

    def __repr__(self):
        return f"<Address {self.uid} - {self.address}>"