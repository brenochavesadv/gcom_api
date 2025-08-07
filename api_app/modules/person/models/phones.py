from datetime import datetime
from pytz import UTC
from main import db
from sqlalchemy.orm import relationship

class Phones(db.Model):
    __bind_key__ = 'main'  # SQLAlchemy to use the 'main' bind
    __tablename__ = "telefones"
    
    id = db.Column('telefones_id', db.Integer, primary_key=True)
    is_active = db.Column('situacao', db.Integer, primary_key=False)
    person_control_id_fk = db.Column('pescod_id_fk', db.Integer, db.ForeignKey('pescod.pescod_id'))
    is_main = db.Column('principal', db.Integer, primary_key=False) 
    phone = db.Column('tel', db.String, primary_key=False)
    created_at = db.Column('data_criacao', db.TIMESTAMP(timezone=True), primary_key=False)
    updated_at = db.Column('data_atualizacao', db.TIMESTAMP(timezone=True), primary_key=False)

    person_control = relationship("PersonControl", back_populates="phones")

    def to_dict(self):
        """Convert model to dictionary using direct attribute access"""
        return {    
            'id': self.id,
            'person_control_id_fk': self.person_control_id_fk,
            'is_active': bool(self.is_active) if self.is_active == 1 else False,
            'phone': self.phone,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    person_control = relationship("PersonControl", back_populates="phones")

    def __repr__(self):
        return f"<Phones {self.id} - {self.phone}>"
    
    def __str__(self):
        return f"Phones(id={self.id}, phone={self.phone}, person_control_id_fk={self.person_control_id_fk})"        