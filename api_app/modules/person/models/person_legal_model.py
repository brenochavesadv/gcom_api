from datetime import datetime
from pytz import UTC
from main import db
from sqlalchemy.orm import relationship

class PersonLegal(db.Model):
    #__bind_key__ = 'main'  # SQLAlchemy to use the 'main' bind
    __tablename__ = "pesjur"

    id = db.Column("pesjur_id", db.Integer, primary_key=True)
    uid = db.Column(db.String(36), unique=True)  # UUID for external reference
    person_id_fk = db.Column("pescod_id_fk", db.Integer, db.ForeignKey('pescod.pescod_id'))
    person_uid_fk = db.Column(db.String(36), db.ForeignKey('pescod.uid'))
    commercial_name = db.Column("fantasia", db.String(50), nullable=True, default=None)
    segment = db.Column("ramo", db.String(255), nullable=True, default=None)
    tax_state_id = db.Column("inscricao_estadual", db.String(20), nullable=True, default=None)
    tax_city_id = db.Column("inscricao_municipal", db.String(20), nullable=True, default=None)
    person_legal_type = db.Column("tipo", db.SmallInteger, nullable=False, default=1)
    share_capital = db.Column("capsocial", db.Numeric(15, 2), nullable=False, default=0.00)
    revenue = db.Column("faturamento", db.Numeric(15, 2), nullable=False, default=0.00)
    tax_regime = db.Column("tribut", db.SmallInteger, nullable=True, default=0)
    contact_name = db.Column("contato", db.String(25), nullable=True, default=None)
    foundation_date = db.Column("data_abertura", db.Date, nullable=True, default=None)
    created_at = db.Column("data_criacao", db.TIMESTAMP(timezone=True))
    updated_at = db.Column("data_atualizacao", db.TIMESTAMP(timezone=True))
    # Add the missing relationship
    person= relationship("Person", back_populates="person_legal", foreign_keys=[person_id_fk])

    def to_dict(self):
        """Convert model to dictionary using direct attribute access"""
        result = {
            'id': self.id,
            'uid': self.uid,
            'person_id_fk': self.person_id_fk,
            'person_uid_fk': self.person_uid_fk,
            'commercial_name': self.commercial_name if self.commercial_name is not None else "",
            'segment': self.segment if self.segment is not None else "",
            'tax_state_id': self.tax_state_id if self.tax_state_id is not None else "",
            'tax_city_id': self.tax_city_id if self.tax_city_id is not None else "",
            'person_legal_type': self.person_legal_type if self.person_legal_type is not None else 0,
            'share_capital': float(self.share_capital) if self.share_capital is not None else 0,
            'revenue': float(self.revenue) if self.revenue is not None else 0,
            'contact_name': self.contact_name if self.contact_name is not None else "",
            'foundation_date': str(self.foundation_date) if self.foundation_date is not None else "",
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        return result

    def __repr__(self):
        return f"<PersonLegal {self.uid} - {self.person_uid_fk}>"

    def __str__(self):
        return f"PersonLegal(uid={self.uid}, commercial_name={self.commercial_name}, person_uid_fk={self.person_uid_fk})"

    # CREATES A FACTORY FOR person_legal
    def from_json(person_uid_fk, data):
        return PersonLegal(
            id=data.get("id"),
            uid=data.get("uid"),
            person_uid_fk=person_uid_fk,
            person_id_fk=data.get("person_id_fk"),
            commercial_name=data.get("commercial_name"),
            segment=data.get("segment"),
            tax_state_id=data.get("tax_state_id"),
            tax_city_id=data.get("tax_city_id"),
            person_legal_type=data.get("person_legal_type"),
            share_capital=data.get("share_capital"),
            revenue=data.get("revenue"),
            contact_name=data.get("contact_name"),
            foundation_date=data.get("foundation_date"),
        )