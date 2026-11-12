from datetime import datetime
from backend.apps.commerciall_api.main import db
from sqlalchemy.orm import relationship

class PersonNatural(db.Model):
    __bind_key__ = 'DB_MAIN' 
    __tablename__ = "person_natural"

    person_uid_fk = db.Column(db.Integer,db.ForeignKey('pescod.pescod_id'), primary_key=True, )
    id_card = db.Column(db.String(25)) 
    id_issuer = db.Column(db.String(15))
    birth_date = db.Column(db.Date)
    birth_city = db.Column(db.String(80))
    pronoun = db.Column(db.Integer)
    nickname = db.Column(db.String(20))
    gender = db.Column(db.Integer)
    sync_status = db.Column(db.String(10), nullable=False, default='PENDING', comment='PENDING:not synced SYNCED:synced')
    created_at = db.Column(db.TIMESTAMP(timezone=True), default=db.func.now())
    updated_at = db.Column(db.TIMESTAMP(timezone=True), default=db.func.now())

    person = relationship("Person", back_populates="natural", foreign_keys=[person_uid_fk])

    def to_dict(self):
        """Convert model to dictionary using direct attribute access"""
        result = {
            'person_uid_fk': self.person_uid_fk if self.person_uid_fk is not None else 0,
            'id_card': self.id_card if self.id_card is not None else "",
            'id_issuer': self.id_issuer if self.id_issuer is not None else "",
            'birth_date': str(self.birth_date) if self.birth_date is not None else "",
            'birth_city': self.birth_city if self.birth_city is not None else "",
            'pronoun': self.pronoun if self.pronoun is not None else 0,
            'nickname': self.nickname if self.nickname is not None else "",
            'gender': self.gender if self.gender is not None else 0,      
            'sync_status': self.sync_status if self.sync_status is not None else "PENDING",
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }
        return result

    
        
    # FACTORY FOR PERSON_NATURAL
    @staticmethod
    def from_json(data):
        person_natural = PersonNatural(
            id_card=data.get("id_card"),
            id_issuer=data.get("id_issuer"),
            birth_date=data.get("birth_date"),
            birth_city=data.get("birth_city"),
            pronoun=data.get("pronoun"),
            nickname=data.get("nickname"),
            gender=data.get("gender"),
            sync_status=data.get("sync_status", "PENDING"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
        return person_natural
    
    
