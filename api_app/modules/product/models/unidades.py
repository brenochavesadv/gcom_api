from main import db

class Unidades(db.Model):
    __bind_key__ = 'product'  # SQLAlchemy to use the 'product' bind
    __tablename__ = "unidades"

    unidades_id = db.Column(db.Integer, primary_key=True)
    instit_id_fk = db.Column(db.Integer, primary_key=False)
    ativo = db.Column(db.Integer, primary_key=False)
    und = db.Column(db.String, primary_key=False)
    descr = db.Column(db.String, primary_key=False)
    tipo = db.Column(db.Integer, primary_key=False)
