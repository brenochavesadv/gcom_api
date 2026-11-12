from backend.apps.commerciall_api.main import db
from sqlalchemy.orm import relationship
from flask import current_app

from backend.modules.utils.parse_json import ParseJson

class PersonFinancial(db.Model):
    __bind_key__ = 'DB_MAIN' 
    __tablename__ = "person_financial"

    person_uid_fk  = db.Column(db.String(36), db.ForeignKey('pescod.pescod_id'), primary_key=True)
    credit_limit = db.Column(db.Float, nullable=True)
    credit_balance = db.Column(db.Float, nullable=True)
    is_credit_available = db.Column(db.Integer, nullable=True)
    block_exceeding_limit = db.Column(db.Integer, nullable=True)
    sync_status = db.Column(db.String(10), nullable=False, default='PENDING')
    created_at = db.Column(db.TIMESTAMP(timezone=True), nullable=True, default=db.func.now())
    updated_at = db.Column(db.TIMESTAMP(timezone=True), nullable=True, default=db.func.now())

    person = relationship("Person", back_populates="financial", lazy='select', foreign_keys=[person_uid_fk])


    def to_dict(self):
        """Convert model to dictionary using direct attribute access"""
        result = {
            'person_uid_fk': self.person_uid_fk,
            'credit_limit': self.credit_limit,
            'credit_balance': self.credit_balance,
            'is_credit_available': ParseJson.return_int_for_true(self.is_credit_available, 1),
            'block_exceeding_limit': self.block_exceeding_limit,
            'sync_status': self.sync_status,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            
        }
        return result

    # CREATES A FACTORY FOR person_financial
    @staticmethod
    def from_json(data):
        current_app.logger.debug(f"Received person financial data: {data}")

        return PersonFinancial(
            person_uid_fk=data.get("person_uid_fk"),
            credit_limit=data.get("credit_limit"),
            credit_balance=data.get("credit_balance"),
            is_credit_available=data.get("is_credit_available"),
            block_exceeding_limit=data.get("block_exceeding_limit"),
            sync_status=data.get("sync_status"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
