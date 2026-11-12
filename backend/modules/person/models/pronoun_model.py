from datetime import datetime
from backend.apps.commerciall_api.main import db
from sqlalchemy.orm import relationship

class Pronoun(db.Model):
    __bind_key__ = 'DB_MAIN' 
    __tablename__ = "pronoun"

    uid = db.Column(db.Integer, primary_key=True)
    pt_br = db.Column(db.String(20))
    pt_br_abbrev = db.Column(db.String(3))

    # add reciprocal relationship name that matches Person.pronoun's back_populates
    #persons = relationship("Person", back_populates="pronoun", lazy='select')
