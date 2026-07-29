from datetime import datetime
from main import db
from sqlalchemy.orm import relationship

class PersonLegalPartner(db.Model):
    __bind_key__ = 'DB_MAIN'
    __tablename__ = 'person_legal_partner'

    uid = db.Column(db.String(36), nullable=False, primary_key=True)
    person_uid_fk = db.Column(db.String(36), db.ForeignKey('pescod.pescod_id'))
    is_active = db.Column(db.SmallInteger, nullable=False, default=0, comment='1:active')
    name = db.Column(db.String(80), nullable=False)
    id_number = db.Column(db.String(20), nullable=False)
    share_percentage = db.Column(db.Float, nullable=False, default=0.0)
    iso2alpha = db.Column(db.String(2), nullable=False)
    age_group = db.Column(db.String(30))
    qualification = db.Column(db.String(50))
    partner_identifier_code = db.Column(db.SmallInteger)
    representative_name = db.Column(db.String(80))
    representative_id_number = db.Column(db.String(20))
    representative_qualification = db.Column(db.String(50))
    admission_date = db.Column(db.String(10))
    sync_status = db.Column(db.String(10), nullable=False, default='PENDING')
    created_at = db.Column(db.TIMESTAMP(timezone=True))
    updated_at = db.Column(db.TIMESTAMP(timezone=True))

    person = relationship("Person", back_populates="person_legal_partner", lazy='select', foreign_keys=[person_uid_fk])

    def to_dict(self):
        """Convert model to dictionary using direct attribute access"""
        return {
            'uid': self.uid,
            'person_uid_fk': self.person_uid_fk,
            'is_active': bool(self.is_active) if self.is_active == 1 else False,
            'name': self.name,
            'id_number': self.id_number,
            'share_percentage': self.share_percentage,
            'iso2alpha': self.iso2alpha,
            'age_group': self.age_group,
            'qualification': self.qualification,
            'partner_identifier_code': self.partner_identifier_code,
            'representative_name': self.representative_name,
            'representative_id_number': self.representative_id_number,
            'representative_qualification': self.representative_qualification,
            'admission_date': self.admission_date,
            'sync_status': self.sync_status,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @staticmethod
    def from_json(data):
        return PersonLegalPartner(
            uid=data.get("uid"),
            person_uid_fk=data.get("person_uid_fk"),
            is_active=int(data.get("is_active")),
            name=data.get("name"),
            id_number=data.get("id_number"),
            share_percentage=float(data.get("share_percentage")),
            iso2alpha=data.get("iso2alpha"),
            age_group=data.get("age_group"),
            qualification=data.get("qualification"),
            partner_identifier_code=int(data.get("partner_identifier_code")),
            representative_name=data.get("representative_name"),
            representative_id_number=data.get("representative_id_number"),
            representative_qualification=data.get("representative_qualification"),
            admission_date=data.get("admission_date"),
            sync_status=data.get("sync_status", "PENDING"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )