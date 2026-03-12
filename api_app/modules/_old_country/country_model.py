from main import db

class Country(db.Model):
    __tablename__ = "paises"

    id = db.Column("id",db.Integer, primary_key=True)
    country_uid = db.Column("id_paises",db.Integer, primary_key=True)
    iso2Code = db.Column(db.String(2), nullable=False)
    iso3Code = db.Column(db.String(3), nullable=False)
    m49Code = db.Column(db.String(3), nullable=False)
    bacenCode = db.Column("cod_bcb", db.Integer)
    bacenTaxFavor = db.Column("trib_fav_bcb", db.Integer)
    phoneCode = db.Column(db.Integer)
    enUs = db.Column(db.String(100), nullable=False)
    ptBr = db.Column("nome",db.String(100), nullable=False)
    esEs = db.Column(db.String(100), nullable=False)
    updated_at = db.Column(db.TIMESTAMP(timezone=True), nullable=False)