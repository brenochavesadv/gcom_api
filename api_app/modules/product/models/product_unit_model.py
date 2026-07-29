from main import db

class ProductUnit(db.Model):
    __bind_key__ = 'DB_MAIN'
    __tablename__ = "unidades"

    uid = db.Column('unidades_id',db.Integer, primary_key=True)
    instit_id_fk = db.Column(db.Integer, nullable=False, default=1) # excluir
    is_active = db.Column('ativo', db.SmallInteger, nullable=False, default=0) # 1 - active
    type = db.Column('tipo', db.SmallInteger, nullable=False, default=1) # 1 - all, 2 - product, 3 - service
    abbrev = db.Column('und', db.String(6), unique=True)
    pt_br = db.Column('descr', db.String(30), unique=True)
    en_us = db.Column('en_us', db.String(30), unique=True)


def to_dict(self):
        return {
            "uid": self.uid,
            "is_active": self.is_active,
            "type": self.type,
            "pt_br": self.pt_br,
            "abbrev": self.abbrev,
            "en_us": self.en_us
        }

""" # factory method
@staticmethod
def from_json(**kwargs):
        return ProductUnit(
            uid=kwargs.get("uid"),
            is_active=kwargs.get("is_active"),
            type=kwargs.get("type"),
            instit_id_fk=kwargs.get("instit_id_fk"),
            pt_br=kwargs.get("pt_br"),
            abbrev=kwargs.get("abbrev"),
            en_us=kwargs.get("en_us")
        ) """