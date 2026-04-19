from datetime import datetime
from pytz import UTC
from main import db
from sqlalchemy.orm import relationship

class Phone(db.Model):
    __bind_key__ = 'DB_MAIN' 
    __tablename__ = "telefones"
    
    id = db.Column('telefones_id', db.Integer, primary_key=True)
    uid = db.Column(db.String(36), unique=True)  # UUID for external reference
    person_id_fk = db.Column('pescod_id_fk', db.Integer, db.ForeignKey('pescod.pescod_id'))
    person_uid_fk = db.Column(db.String(36), db.ForeignKey('pescod.uid'))
    is_active = db.Column('situacao', db.SmallInteger, nullable=False, default=0, comment='1=active, 0=not')
    is_main = db.Column('principal', db.SmallInteger, nullable=False, default=0, comment='1=main, 0=not')
    phone = db.Column('tel', db.String(20))
    iso2alpha = db.Column(db.String(3))
    phone_type = db.Column(db.String(12))
    observation = db.Column(db.String(30))
    created_at = db.Column('data_criacao', db.TIMESTAMP(timezone=True))
    updated_at = db.Column('data_atualizacao', db.TIMESTAMP(timezone=True))

    person = relationship("Person", back_populates="phone", foreign_keys=[person_uid_fk])
    
    def to_dict(self):
        """Convert model to dictionary using direct attribute access"""
        return {    
            'uid': self.uid,
            'person_uid_fk': self.person_uid_fk,
            'is_active': bool(self.is_active) if self.is_active == 1 else False,
            'is_main': bool(self.is_main) if self.is_main == 1 else False,
            'phone': self.phone,
            'iso2alpha': self.iso2alpha,
            'phone_type': self.phone_type,
            'observation': self.observation,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }
    
    def __repr__(self):
        return f"<Phone {self.uid} - {self.phone}>"
    
    def __str__(self):
        return f"Phone(uid={self.uid}, phone={self.phone}, person_uid_fk={self.person_uid_fk})"        