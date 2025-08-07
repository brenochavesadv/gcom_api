from datetime import datetime
from pytz import UTC
from main import db
from sqlalchemy.orm import relationship

class Address(db.Model):
    __bind_key__ = 'main'  # SQLAlchemy to use the 'main' bind
    __tablename__ = "enderecos"

    id = db.Column('enderecos_id', db.Integer, primary_key=True)
    is_active = db.Column('situacao', db.Integer, nullable=False, default=1, comment='1 = ativo 0 = inativo')
    is_main = db.Column('principal', db.Boolean, nullable=False, default=False, comment='Indicates if this is the main address for the person')
    person_control_id_fk = db.Column('pescod_id_fk', db.Integer, db.ForeignKey('pescod.pescod_id'), nullable=False, default=0)
    address_label = db.Column('apelido', db.String(50), nullable=True, comment='Label for the address, e.g., "Home", "Office"')
    address_type_id_fk = db.Column('logradouros_id_fk', db.Integer, db.ForeignKey('logradouros.Id'), nullable=False, default=1, comment='tipo logradouro')
    address = db.Column('logradouro', db.String(100), nullable=True)
    number = db.Column('numero', db.String(8), nullable=True)
    complement = db.Column('complemento', db.String(50), nullable=True)
    nbhd = db.Column('bairro', db.String(40), nullable=True)
    zip_code = db.Column('cep', db.String(10), nullable=True)
    city_id_fk = db.Column('municipios_id_fk', db.Integer, nullable=False, default=1827)
    codigo_ibge_municipio = db.Column('codigo_ibge_municipio', db.Integer, nullable=True)
    city = db.Column(db.String(60), nullable=True, comment='City name')
    state = db.Column(db.String(50), nullable=True, comment='State abbreviation')
    country = db.Column(db.String(50), nullable=True, comment='Country name')
    created_at = db.Column('data_criacao', db.TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=True)
    updated_at = db.Column('data_atualizacao', db.TIMESTAMP(timezone=True), nullable=True)

    person_control = relationship("PersonControl", back_populates="addresses")
    address_type = relationship("AddressType", back_populates="addresses")

    def to_dict(self):
        """Convert model to dictionary using direct attribute access"""
        result = {
            'id': self.id,
            'is_active': bool(self.is_active) if self.is_active == 1 else False,
            'is_main': self.is_main,
            'person_control_id_fk': self.person_control_id_fk,
            'address_label': self.address_label if self.address_label is not None else "",
            'address_type_id_fk': self.address_type_id_fk,
            'address': self.address if self.address is not None else "",
            'number': self.number if self.number is not None else "",
            'complement': self.complement if self.complement is not None else "",
            'nbhd': self.nbhd if self.nbhd is not None else "",
            'zip_code': self.zip_code if self.zip_code is not None else "",
            'codigo_ibge_municipio': self.codigo_ibge_municipio,
            'city': self.city if self.city is not None else "",
            'state': self.state if self.state is not None else "",
            'country': self.country if self.country is not None else "",
            'city_id_fk': self.city_id_fk,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }
        return result

    def __repr__(self):
        return f"<Address {self.id} - {self.address}>"

class AddressType(db.Model):
    __bind_key__ = 'main'  # SQLAlchemy to use the 'main' bind
    __tablename__ = "logradouros"

    id = db.Column('Id', db.Integer, primary_key=True)
    name = db.Column('logr', db.String(20), nullable=True)
    abbreviation = db.Column('abrev', db.String(5), nullable=True)

    addresses = relationship("Address", back_populates="address_type")

    def to_dict(self):
        """Convert model to dictionary using direct attribute access"""
        result = {
            'id': self.id,
            'name': self.name,
            'abbreviation': self.abbreviation
        }
        return result
    
    def __repr__(self):
        return f"<AddressType {self.id} - {self.name}>"