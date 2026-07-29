from main import db
from sqlalchemy.orm import relationship
from flask import current_app

class PersonLegal(db.Model):
    __bind_key__ = 'DB_MAIN' 
    __tablename__ = "pesjur"

    uid = db.Column("pesjur_id", db.Integer, primary_key=True)
    person_uid_fk = db.Column("pescod_id_fk", db.Integer, db.ForeignKey('pescod.pescod_id'))
    commercial_name = db.Column("fantasia", db.String(50), nullable=True, default=None)
    person_legal_type = db.Column("tipo", db.String(40), nullable=True, default=None)
    share_capital = db.Column("capsocial", db.Numeric(15, 2), nullable=False, default=0.00)
    revenue = db.Column("faturamento", db.Numeric(15, 2), nullable=False, default=0.00)
    person_legal_size = db.Column(db.String(30), nullable=True, default=None)
    register_status = db.Column(db.SmallInteger, nullable=False, default=0)
    register_status_reason = db.Column(db.String(80), nullable=True, default=None)
    register_status_date = db.Column(db.Date, nullable=True, default=None)
    special_situation = db.Column(db.String(40), nullable=True, default=None)
    special_situation_date = db.Column(db.Date, nullable=True, default=None)
    is_headquarter = db.Column(db.SmallInteger, nullable=False, default=0)
    is_simples_regime = db.Column(db.SmallInteger, nullable=False, default=0)
    simples_admission_date = db.Column(db.Date, nullable=True, default=None)
    simples_exclusion_date = db.Column(db.Date, nullable=True, default=None)
    is_mei_regime = db.Column(db.SmallInteger, nullable=False, default=0)
    mei_admission_date = db.Column(db.Date, nullable=True, default=None)
    mei_exclusion_date = db.Column(db.Date, nullable=True, default=None)
    contact_name = db.Column("contato", db.String(25), nullable=True, default=None)
    foundation_date = db.Column("data_abertura", db.Date, nullable=True, default=None)    
    tax_state_id = db.Column("inscricao_estadual", db.String(20), nullable=True, default=None)
    tax_city_id = db.Column("inscricao_municipal", db.String(20), nullable=True, default=None)
    responsible_entity = db.Column(db.String(70), nullable=True, default=None)

    # Add the missing relationship
    person= relationship("Person", back_populates="person_legal", foreign_keys=[person_uid_fk])

    def to_dict(self):
        """Convert model to dictionary using direct attribute access"""
        result = {
            'uid': self.uid,
            'person_uid_fk': self.person_uid_fk,
            'commercial_name': self.commercial_name if self.commercial_name is not None else "",
            'person_legal_type': self.person_legal_type,
            'share_capital': float(self.share_capital) if self.share_capital is not None else 0.00,
            'revenue': float(self.revenue) if self.revenue is not None else 0.00,
            'person_legal_size': self.person_legal_size,
            'register_status': self.register_status,
            'register_status_reason': self.register_status_reason if self.register_status_reason is not None else "",
            'register_status_date': self.register_status_date if self.register_status_date is not None else "",
            'special_situation': self.special_situation if self.special_situation is not None else "",
            'special_situation_date': self.special_situation_date if self.special_situation_date is not None else "",
            'is_headquarter': bool(self.is_headquarter) if self.is_headquarter == 1 else False,
            'is_simples_regime': bool(self.is_simples_regime) if self.is_simples_regime == 1 else False,
            'simples_admission_date': self.simples_admission_date if self.simples_admission_date is not None else "",
            'simples_exclusion_date': self.simples_exclusion_date if self.simples_exclusion_date is not None else "",
            'is_mei_regime': bool(self.is_mei_regime) if self.is_mei_regime == 1 else False,
            'mei_admission_date': self.mei_admission_date if self.mei_admission_date is not None else "",
            'mei_exclusion_date': self.mei_exclusion_date if self.mei_exclusion_date is not None else "",
            'contact_name': self.contact_name if self.contact_name is not None else "",
            'foundation_date': self.foundation_date if self.foundation_date is not None else "",
            'tax_state_id': self.tax_state_id if self.tax_state_id is not None else "",
            'tax_city_id': self.tax_city_id if self.tax_city_id is not None else "",
            'responsible_entity': self.responsible_entity if self.responsible_entity is not None else "",
        }
        return result

    # CREATES A FACTORY FOR person_legal
    @staticmethod
    def from_json(data):
        current_app.logger.debug(f"Received person legal data: {data}")

        return PersonLegal(
            commercial_name=data.get("commercial_name"),
            person_legal_type=data.get("person_legal_type"),
            share_capital=float(data.get("share_capital")) if data.get("share_capital") else 0.00,
            revenue=float(data.get("revenue")) if data.get("revenue") else 0.00,
            person_legal_size=data.get("person_legal_size"),
            register_status=data.get("register_status"),
            register_status_reason=data.get("register_status_reason"),
            register_status_date=data.get("register_status_date"),
            special_situation=data.get("special_situation"),
            special_situation_date=data.get("special_situation_date"),
            is_headquarter=1 if data.get("is_headquarter") else 0,
            is_simples_regime=1 if data.get("is_simples_regime") else 0,
            simples_admission_date=data.get("simples_admission_date"),
            simples_exclusion_date=data.get("simples_exclusion_date"),
            is_mei_regime=1 if data.get("is_mei_regime") else 0,
            mei_admission_date=data.get("mei_admission_date"),
            mei_exclusion_date=data.get("mei_exclusion_date"),
            contact_name=data.get("contact_name"),
            foundation_date=data.get("foundation_date"),
            tax_state_id=data.get("tax_state_id"),
            tax_city_id=data.get("tax_city_id"),
            responsible_entity=data.get("responsible_entity")
        )

    def updatable_fields(self, other):
        """Update mutable fields from another PersonNatural-like object.

        `other` can be a PersonNatural instance or an object with compatible attributes.
        Only updates fields that are safe to change (no PK/FK).
        """
        _updatable_fields = [
            'commercial_name',
            'person_legal_type',
            'share_capital',
            'revenue',
            'person_legal_size',
            'register_status',
            'register_status_reason',
            'register_status_date',
            'special_situation',
            'special_situation_date',
            'is_headquarter',
            'is_simples_regime',
            'simples_admission_date',
            'simples_exclusion_date',
            'is_mei_regime',
            'mei_admission_date',   
            'mei_exclusion_date',
            'contact_name',
            'foundation_date',
            'tax_state_id',
            'tax_city_id',
            'responsible_entity'
        ]

        for field in _updatable_fields:
            if hasattr(other, field):
                setattr(self, field, getattr(other, field))