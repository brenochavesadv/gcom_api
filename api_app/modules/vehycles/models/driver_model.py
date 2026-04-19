from sqlalchemy import func
from sqlalchemy.orm import relationship
from main import db
from sqlalchemy.dialects.mysql import LONGTEXT
from ...users.models.organization_model import Organization
from ...person.models.person_model import Person

class Driver(db.Model):
    __bind_key__ = 'DB_FROTALL'
    __tablename__ = "drivers"

    uid = db.Column(db.String(36), primary_key=True, unique=True)
    organization_uid_fk = db.Column(db.String(36), db.ForeignKey(Organization.uid))
    is_active = db.Column(db.Integer, default=0)  # 1 for active, 0 for inactive
    person_uid_fk = db.Column(db.String(36), db.ForeignKey(Person.uid))
    nickname = db.Column(db.String(20), nullable=False)
    sync_status = db.Column(db.String(10))
    created_at = db.Column(db.TIMESTAMP, server_default=func.now())
    updated_at = updated_at = db.Column(db.TIMESTAMP, default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            'uid': self.uid,
            'organization_uid_fk': self.organization_uid_fk,
            'is_active': bool(self.is_active) if self.is_active == 1 else False,
            'person_uid_fk': self.person_uid_fk,
            'nickname': self.nickname,
            'sync_status': self.sync_status,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }

    