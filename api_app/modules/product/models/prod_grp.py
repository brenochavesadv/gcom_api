from main import db

class ProdGrp(db.Model):
    __bind_key__ = 'product'  # SQLAlchemy to use the 'product' bind
    __tablename__ = "prod_grp"

    prod_grp_id = db.Column(db.Integer, primary_key=True)
    instit_id_fk = db.Column(db.Integer, primary_key=False)
    niv = db.Column(db.Integer, primary_key=False)
    nv1 = db.Column(db.String, primary_key=False)
    nv2 = db.Column(db.String, primary_key=False)
    nv1id = db.Column(db.Integer, primary_key=False)
    nv3 = db.Column(db.String, primary_key=False)
    nv2id = db.Column(db.Integer, primary_key=False)
    data_atz = db.Column(db.DateTime, primary_key=False)
