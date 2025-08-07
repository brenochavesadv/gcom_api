from main import db
from datetime import datetime

class Aliquota(db.Model):
    __bind_key__ = 'product'  # SQLAlchemy to use the 'product' bind
    __tablename__ = "aliquotas"

    aliquotas_id = db.Column(db.Integer, primary_key=True)
    instit_id_fk = db.Column(db.Integer, nullable=False, default=0)
    descr = db.Column(db.String(6), nullable=False, default="")
    bematech = db.Column(db.String(2), nullable=False, default="")
    valor = db.Column(db.Numeric(5, 2), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
