from datetime import datetime
from main import db
from sqlalchemy.orm import relationship

class Mail(db.Model):
    __bind_key__ = 'DB_MAIN' 
    __tablename__ = "mails"

    uid = db.Column('mails_id', db.Integer, primary_key=True)
    person_uid_fk = db.Column('pescod_id_fk', db.Integer, db.ForeignKey('pescod.pescod_id'))
    is_active = db.Column('situacao', db.SmallInteger, nullable=False, default=0, comment='1:active 0:not')
    email = db.Column(db.String(100), nullable=False, comment='Email address')
    is_main = db.Column('principal', db.SmallInteger, nullable=False, default=0, comment='1:main email 0:not')
    sync_status = db.Column(db.String(10), nullable=False, default='PENDING', comment='PENDING:not synced SYNCED:synced')
    created_at = db.Column('data_criacao', db.TIMESTAMP(timezone=True))
    updated_at = db.Column('data_atualizacao', db.TIMESTAMP(timezone=True))

    person = relationship("Person", back_populates="mail", lazy='select', foreign_keys=[person_uid_fk])

    def to_dict(self):
        """Convert model to dictionary using direct attribute access"""
        return {
            'uid': self.uid,
            'person_uid_fk': self.person_uid_fk,
            'is_active': bool(self.is_active) if self.is_active == 1 else False,
            'email': self.email,
            'is_main': bool(self.is_main) if self.is_main == 1 else False,
            'sync_status': self.sync_status,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def __repr__(self):
        return f"<Mail {self.uid} - {self.email}>"

    def __str__(self):
        return f"Mail(uid={self.uid}, email={self.email}, person_uid_fk={self.person_uid_fk})"

    @staticmethod
    def from_json(data):
        return Mail(
            uid=int(data.get("uid")) if data.get("uid") else None,
            person_uid_fk=int(data.get("person_uid_fk")) if data.get("person_uid_fk") not in (None, "") else None,
            is_active=1 if data.get("is_active") else 0,
            email=data.get("email"),
            is_main=1 if data.get("is_main") else 0,
            sync_status=data.get("sync_status", "PENDING"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )