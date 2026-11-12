from datetime import datetime
from backend.apps.commerciall_api.main import db
from sqlalchemy.orm import relationship

from backend.modules.utils.parse_json import ParseJson

class PersonLegalActivity(db.Model):
    __bind_key__ = 'DB_MAIN'
    __tablename__ = 'person_legal_activity'

    uid = db.Column(db.String(36), nullable=False, primary_key=True)
    person_uid_fk = db.Column(db.String(36), db.ForeignKey('pescod.pescod_id'))
    activity_code = db.Column(db.String(10), nullable=False)
    is_main = db.Column(db.SmallInteger, nullable=False, default=0, comment='1:main')
    is_active = db.Column(db.SmallInteger, nullable=False, default=0, comment='1:active')
    description = db.Column(db.String(100), nullable=False)
    sync_status = db.Column(db.String(10), nullable=False, default='PENDING', comment='PENDING:not synced SYNCED:synced')
    created_at = db.Column(db.TIMESTAMP(timezone=True), default=db.func.now())
    updated_at = db.Column(db.TIMESTAMP(timezone=True), default=db.func.now())

    person = relationship("Person", back_populates="activities", lazy='select', foreign_keys=[person_uid_fk])

    def to_dict(self):
        """Convert model to dictionary using direct attribute access"""
        return {
            'uid': self.uid,
            'person_uid_fk': self.person_uid_fk,
            'activity_code': self.activity_code,
            'is_main': ParseJson.return_int_for_true(self.is_main, 1),
            'is_active': ParseJson.return_int_for_true(self.is_active, 1),
            'description': self.description,
            'sync_status': self.sync_status,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def __repr__(self):
        return f"<PersonLegalActivity {self.uid} - {self.description}>"

    def __str__(self):
        return f"PersonLegalActivity(uid={self.uid}, description={self.description}, person_uid_fk={self.person_uid_fk})"

    @staticmethod
    def from_json(data):
        return PersonLegalActivity(
            uid=data.get("uid"),
            person_uid_fk=data.get("person_uid_fk"),
            activity_code=data.get("activity_code"),
            is_main=1 if data.get("is_main") else 0,
            is_active=1 if data.get("is_active") else 0,
            description=data.get("description"),
            sync_status=data.get("sync_status", "PENDING"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )