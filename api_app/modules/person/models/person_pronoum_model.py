from datetime import datetime
from main import db
from sqlalchemy.orm import relationship

class PersonPronoun(db.Model):
    __bind_key__ = 'main' 
    __tablename__ = "person_pronouns"

    id = db.Column(db.Integer, primary_key=True)
    pt_BR = db.Column(db.String, primary_key=False)

    person_control = relationship("PersonNatural", back_populates="pronouns")