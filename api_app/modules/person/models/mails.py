from datetime import datetime
from main import db
from sqlalchemy.orm import relationship

class Mails(db.Model):
    __bind_key__ = 'main' 
    __tablename__ = "mails"

    id = db.Column('mails_id', db.Integer, primary_key=True)
    person_control_id_fk = db.Column('pescod_id_fk', db.Integer, db.ForeignKey('pescod.pescod_id'))
    is_active = db.Column('situacao', db.Integer, primary_key=False)
    email = db.Column('email', db.String, primary_key=False)
    is_main = db.Column('principal', db.Integer, primary_key=False)
    created_at = db.Column('data_criacao', db.TIMESTAMP(timezone=True), primary_key=False)
    updated_at = db.Column('data_atualizacao', db.TIMESTAMP(timezone=True), primary_key=False)

    person_control = relationship("PersonControl", back_populates="mails")

    def to_dict(self):
        """Convert model to dictionary using direct attribute access"""
        return {
            'id': self.id,
            'person_control_id_fk': self.person_control_id_fk,
            'is_active': bool(self.is_active) if self.is_active == 1 else False,
            'email': self.email,
            'is_main': bool(self.is_main) if self.is_main == 1 else False,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else str(self.created_at)
        }

    def __repr__(self):
        return f"<Mails {self.id} - {self.mail}"

    def __str__(self):
        return f"Mails(id={self.id}, mail={self.mail}, person_control_id_fk={self.person_control_id_fk})"