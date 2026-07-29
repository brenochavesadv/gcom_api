from datetime import datetime
from main import db
from sqlalchemy.orm import relationship

class PersonLegalBrTaxRegime(db.Model):
    __bind_key__ = 'DB_MAIN'
    __tablename__ = 'person_legal_br_tax_regime'

    uid = db.Column(db.String(36), nullable=False, primary_key=True)
    person_uid_fk = db.Column(db.String(36), db.ForeignKey('pescod.pescod_id'))
    tax_regime = db.Column(db.String(40), nullable=False)
    year = db.Column(db.String(4), nullable=False)
    scp_cnpj= db.Column(db.String(18), nullable=False)
    accounting_records = db.Column(db.SmallInteger, nullable=False, default=0)
    sync_status = db.Column(db.String(10), nullable=False, default='PENDING', comment='PENDING:not synced SYNCED:synced')
    created_at = db.Column(db.TIMESTAMP(timezone=True))
    updated_at = db.Column(db.TIMESTAMP(timezone=True))

    person = relationship("Person", back_populates="person_legal_br_tax_regime", lazy='select', foreign_keys=[person_uid_fk])

    def to_dict(self):
        """Convert model to dictionary using direct attribute access"""
        return {
            'uid': self.uid,
            'person_uid_fk': self.person_uid_fk,
            'tax_regime': self.tax_regime,
            'year': self.year,
            'scp_cnpj': self.scp_cnpj,
            'accounting_records': self.accounting_records,
            'sync_status': self.sync_status,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def __repr__(self):
        return f"<PersonLegalBrTaxRegime {self.uid} - {self.tax_regime}>"

    def __str__(self):
        return f"PersonLegalBrTaxRegime(uid={self.uid}, tax_regime={self.tax_regime}, person_uid_fk={self.person_uid_fk})"

    @staticmethod
    def from_json(data):
        return PersonLegalBrTaxRegime(
            uid=data.get("uid"),
            person_uid_fk=data.get("person_uid_fk"),
            tax_regime=data.get("tax_regime"),
            year=data.get("year"),
            scp_cnpj=data.get("scp_cnpj"),
            accounting_records=int(data.get("accounting_records")),
            sync_status=data.get("sync_status", "PENDING"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )