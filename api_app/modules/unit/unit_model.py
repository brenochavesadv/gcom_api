from main import db
from sqlalchemy.orm import relationship


class Unit(db.Model):
    __bind_key__ = 'DB_MAIN' 
    __tablename__ = "unidades"
    
    unit_uid = db.Column("unidades_id", db.Integer, primary_key=True, autoincrement=True)
    organization_uid_fk = db.Column("instit_id_fk", db.Integer, nullable=False, default=0)
    is_active = db.Column("ativo", db.Integer, nullable=False, default=1)
    abbreviation = db.Column("und", db.String(2), nullable=False)
    description = db.Column("descr", db.String(12), nullable=False, default='')
    type = db.Column("tipo", db.Integer, nullable=False, default=0)

    def to_dict(self):
        return {
            "unit_uid": self.unit_uid,
            "organization_uid_fk": self.organization_uid_fk,
            "is_active": True if self.is_active == 1 else False,
            "abbreviation": self.abbreviation,
            "description": self.description,
            "type": self.type
        }

    def __repr__(self):
        return f"<Unit {self.unit_uid}>"

    def __str__(self):
        return self.description
    
    def create(**kwargs):
        return Unit(
            organization_uid_fk=kwargs.get("organization_uid_fk"),
            is_active=kwargs.get("is_active"),
            abbreviation=kwargs.get("abbreviation"),
            description=kwargs.get("description"),
            type=kwargs.get("type")
        )