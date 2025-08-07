from datetime import datetime
from pytz import UTC
from main import db
from sqlalchemy.orm import relationship

class PersonLegal(db.Model):
    __bind_key__ = 'main'  # SQLAlchemy to use the 'main' bind
    __tablename__ = "pesjur"

    id = db.Column("pesjur_id", db.Integer, primary_key=True)
    person_control_id_fk = db.Column("pescod_id_fk", db.Integer, db.ForeignKey('pescod.pescod_id'))
    commercialName = db.Column("nome_fantasia", db.String, primary_key=False)
    segment = db.Column("ramo", db.String, primary_key=False)
    idTaxCity = db.Column("inscricao_estadual", db.String, primary_key=False)
    idTaxState = db.Column("inscricao_municipal", db.String, primary_key=False)
    type = db.Column("tipo", db.Integer, primary_key=False)
    shareCapital = db.Column("capital_social", db.Numeric, primary_key=False)
    revenue = db.Column("faturamento", db.Numeric, primary_key=False)
    tax = db.Column("tribut", db.Integer, primary_key=False)
    contactName = db.Column("contato", db.String, primary_key=False)

    # Add the missing relationship
    person_control = relationship("PersonControl", back_populates="person_legal")
    phones = relationship("Phones", backref="person_legal", lazy='dynamic')
    addresses = relationship("Addresses", backref="person_legal", lazy='dynamic')

    def to_dict(self):
        """Convert model to dictionary using direct attribute access"""
        result = {
            'id': self.id,
            'person_control_id_fk': self.person_control_id_fk,
            'commercialName': self.commercialName,
            'segment': self.segment,
            'idTaxCity': self.idTaxCity,
            'idTaxState': self.idTaxState,
            'type': self.type,
            'shareCapital': float(self.shareCapital) if self.shareCapital is not None else None,
            'revenue': float(self.revenue) if self.revenue is not None else None,
            'tax': self.tax,
            'contactName': self.contactName,
        }
        return result

    def __repr__(self):
        return f"<PersonLegal {self.id} - {self.commercialName}>"