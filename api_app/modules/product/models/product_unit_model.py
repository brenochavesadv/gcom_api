from main import db

class ProductUnit(db.Model):
    __bind_key__ = 'sales'  # SQLAlchemy to use the 'product' bind
    __tablename__ = "unidades"

    unidades_id = db.Column(db.Integer, primary_key=True)
    instit_id_fk = db.Column(db.Integer)
    ativo = db.Column(db.Integer)
    und = db.Column(db.String(3))
    descr = db.Column(db.String(20))
    tipo = db.Column(db.Integer)
