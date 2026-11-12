from backend.apps.commerciall_api.main import db

class Cfop(db.Model):
    __bind_key__ = 'DB_MAIN'  # SQLAlchemy to use the 'product' bind
    __tablename__ = "product_tax_br_cfop"

    cfop = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    
    def to_dict(self):
        return {
            "cfop": self.cfop,
            "description": self.description
        }

    @staticmethod
    def from_json(data):
        return Cfop(
            cfop=data.get("cfop"),
            description=data.get("description")
        )