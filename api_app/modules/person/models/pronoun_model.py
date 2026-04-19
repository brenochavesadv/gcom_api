from datetime import datetime
from main import db
from sqlalchemy.orm import relationship

class Pronoun(db.Model):
    __bind_key__ = 'DB_MAIN' 
    __tablename__ = "pronoun"

    uid = db.Column(db.Strin(14), primary_key=True)
    pt_br = db.Column(db.String(20))
    pt_br_abbrev = db.Column(db.String(3))
    updated_at = db.Column(db.TIMESTAMP(timezone=True))

    # add reciprocal relationship name that matches Person.pronoun's back_populates
    #persons = relationship("Person", back_populates="pronoun", lazy='select')