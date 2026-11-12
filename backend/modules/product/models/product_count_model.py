from backend.apps.commerciall_api.main import db

class ProductCount(db.Model):
    __bind_key__ = 'DB_MAIN' 
    __tablename__ = "product_count"

    uid = db.Column(db.Integer, primary_key=True)
    product_uid_fk = db.Column(db.Integer, db.ForeignKey("produtos.produtos_id"), nullable=False)
    current_tax_inventory = db.Column(db.Numeric, nullable=False)
    current_front_inventory = db.Column(db.Numeric, nullable=False)
    current_warehouse_inventory = db.Column(db.Numeric, nullable=False)
    audited_tax_inventory = db.Column(db.Numeric, nullable=False)
    audited_front_inventory = db.Column(db.Numeric, nullable=False)
    audited_warehouse_inventory = db.Column(db.Numeric, nullable=False)
    user_uid_fk = db.Column(db.String(36), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

    product = db.relationship("Product", back_populates="product_count", lazy=True)

def to_dict(self):
        return {
            "uid": self.uid,
            "product_uid_fk": self.product_uid_fk,
            "current_tax_inventory": float(self.current_tax_inventory),
            "current_front_inventory": float(self.current_front_inventory),
            "current_warehouse_inventory": float(self.current_warehouse_inventory),
            "audited_tax_inventory": float(self.audited_tax_inventory),
            "audited_front_inventory": float(self.audited_front_inventory),
            "audited_warehouse_inventory": float(self.audited_warehouse_inventory),
            "user_uid_fk": self.user_uid_fk,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

@staticmethod
def from_json(**kwargs):
        return ProductCount(
            uid=kwargs.get("uid"),
            product_uid_fk=kwargs.get("product_uid_fk"),
            current_tax_inventory=kwargs.get("current_tax_inventory"),
            current_front_inventory=kwargs.get("current_front_inventory"),
            current_warehouse_inventory=kwargs.get("current_warehouse_inventory"),
            audited_tax_inventory=kwargs.get("audited_tax_inventory"),
            audited_front_inventory=kwargs.get("audited_front_inventory"),
            audited_warehouse_inventory=kwargs.get("audited_warehouse_inventory"),
            user_uid_fk=kwargs.get("user_uid_fk"),
            created_at=kwargs.get("created_at")
        )
