from main import db

class Fabpro(db.Model):
    __bind_key__ = 'product'  # SQLAlchemy to use the 'product' bind
    __tablename__ = "fabpro"

    fabpro_id = db.Column(db.Integer, primary_key=True)
    instit_id_fk = db.Column(db.Integer, primary_key=False)
    marca = db.Column(db.String, primary_key=False)
    fabr = db.Column(db.String, primary_key=False)
