from backend.apps.commerciall_api.main import db
from sqlalchemy.orm import relationship
from flask import current_app

from backend.modules.utils.parse_json import ParseJson

class PersonAccounts(db.Model):
    __bind_key__ = 'DB_MAIN' 
    __tablename__ = "person_accounts"

    uid = db.Column(db.String(36), primary_key=True)
    person_uid_fk = db.Column(db.String(36),db.ForeignKey('pescod.pescod_id'))
    is_active = db.Column(db.SmallInteger, nullable=False, default=0, comment='1:active')
    sync_status = db.Column(db.String(10), nullable=False, default='PENDING')
    created_at = db.Column(db.TIMESTAMP(timezone=True), nullable=True , default=db.func.now())
    updated_at = db.Column(db.TIMESTAMP(timezone=True), nullable=True, default=db.func.now())

    person = relationship("Person", back_populates="accounts", lazy='select', foreign_keys=[person_uid_fk])

    def to_dict(self):
        """Convert model to dictionary using direct attribute access"""
        result = {
            'uid': self.uid,
            'person_uid_fk': self.person_uid_fk,
            'is_active': ParseJson.return_int_for_true(self.is_active, 2),
            'sync_status': self.sync_status,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            
        }
        return result

    # CREATES A FACTORY FOR person_legal
    @staticmethod
    def from_json(data):
        current_app.logger.debug(f"Received person legal data: {data}")

        return PersonAccounts(
            uid=data.get("uid"),
            person_uid_fk=data.get("person_uid_fk"),
            is_active=data.get("is_active"),
            sync_status=data.get("sync_status"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )