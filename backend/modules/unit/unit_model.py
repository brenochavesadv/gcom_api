from backend.apps.commerciall_api.main import db

class Unit(db.Model):
    __bind_key__ = 'DB_MAIN'
    __tablename__ = "unit"

    id = db.Column(db.SmallInteger, primary_key=True)
    is_active = db.Column(db.SmallInteger, nullable=False, default=0, comment="1: active")
    type = db.Column(db.SmallInteger, nullable=False, default=1, comment="1: all, 2: product, 3: service")
    abbrev_pt_br = db.Column(db.String(6), unique=True)
    pt_br = db.Column(db.String(30), unique=True)
    abbrev_en_us = db.Column(db.String(10), unique=True)
    en_us = db.Column(db.String(30), unique=True)

    def to_dict(self):
        return {
            "id": self.id,
            "is_active": self.is_active,
            "type": self.type,
            "abbrev_pt_br": self.abbrev_pt_br,
            "pt_br": self.pt_br,
            "abbrev_en_us": self.abbrev_en_us,
            "en_us": self.en_us,
        }

    @staticmethod
    def from_json(**kwargs):
        return Unit(
            id=kwargs.get("id"),
            is_active=kwargs.get("is_active"),
            type=kwargs.get("type"),
            pt_br=kwargs.get("pt_br"),
            abbrev_pt_br=kwargs.get("abbrev_pt_br"),
            abbrev_en_us=kwargs.get("abbrev_en_us"),
            en_us=kwargs.get("en_us"),
        )