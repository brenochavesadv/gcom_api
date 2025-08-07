from main import db

class Products(db.Model):
    __bind_key__ = 'product'  # SQLAlchemy to use the 'product' bind
    __tablename__ = "produtos"

    produtos_id = db.Column(db.Integer, primary_key=True)
    instit_matriz_id_fk = db.Column(db.Integer, primary_key=False)
    codprod = db.Column(db.Integer, primary_key=False)
    ativo = db.Column(db.Integer, primary_key=False)
    descr = db.Column(db.String, primary_key=False)
    descres = db.Column(db.String, primary_key=False)
    und = db.Column(db.Integer, primary_key=False)
    prod_grp_id_fk = db.Column(db.Integer, primary_key=False)
    tam = db.Column(db.Numeric, primary_key=False)
    larg = db.Column(db.Numeric, primary_key=False)
    alt = db.Column(db.Numeric, primary_key=False)
    cubag = db.Column(db.Numeric, primary_key=False)
    peso = db.Column(db.Numeric, primary_key=False)
    codbarra = db.Column(db.String, primary_key=False)
    fabr_id_fk = db.Column(db.Integer, primary_key=False)
    forn_pescod_id_fk = db.Column(db.Integer, primary_key=False)
    caract = db.Column(db.String, primary_key=False)
    ncm = db.Column(db.String, primary_key=False)
    cest = db.Column(db.String, primary_key=False)
    desnf = db.Column(db.String, primary_key=False)
    combo = db.Column(db.Integer, primary_key=False)
    foto = db.Column(db.String, primary_key=False)
    img_bites = db.Column(db.Integer, primary_key=False)
    datatz = db.Column(db.DateTime, primary_key=False)
    usuatz = db.Column(db.Integer, primary_key=False)
