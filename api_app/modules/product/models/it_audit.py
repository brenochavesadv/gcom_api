from main import db

class ItAudit(db.Model):
    __bind_key__ = 'product'  # SQLAlchemy to use the 'product' bind
    __tablename__ = "it_audit"

    id = db.Column(db.Integer, primary_key=True)
    instit = db.Column(db.Integer, primary_key=False)
    idprod = db.Column(db.Integer, primary_key=False)
    codprod = db.Column(db.Integer, primary_key=False)
    fiscal_atual = db.Column(db.Numeric, primary_key=False)
    frente_atual = db.Column(db.Numeric, primary_key=False)
    dep_atual = db.Column(db.Numeric, primary_key=False)
    fiscal_audit = db.Column(db.Numeric, primary_key=False)
    frente_audit = db.Column(db.Numeric, primary_key=False)
    dep_audit = db.Column(db.Numeric, primary_key=False)
    compra_audit = db.Column(db.Numeric, primary_key=False)
    custo_audit = db.Column(db.Numeric, primary_key=False)
    lucro_audit = db.Column(db.Numeric, primary_key=False)
    venda1_audit = db.Column(db.Numeric, primary_key=False)
    venda2_audit = db.Column(db.Numeric, primary_key=False)
    venda3_audit = db.Column(db.Numeric, primary_key=False)
    venda4_audit = db.Column(db.Numeric, primary_key=False)
    venda5_audit = db.Column(db.Numeric, primary_key=False)
    usu_audit = db.Column(db.Integer, primary_key=False)
    data_audit = db.Column(db.DateTime, primary_key=False)
