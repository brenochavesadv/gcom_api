from datetime import datetime
from backend.apps.commerciall_api.main import db


class ProductComboItem(db.Model):
    """A product component belonging to a persisted combo."""

    __bind_key__ = "DB_MAIN"
    __tablename__ = "product_combo_item"

    uid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    combo_uid_fk = db.Column(
        db.Integer,
        db.ForeignKey("product_combo.uid"),
        nullable=False,
    )
    product_uid_fk = db.Column(
        db.Integer,
        db.ForeignKey("produtos.produtos_id"),
        nullable=False,
    )
    quantity = db.Column(db.Numeric(10, 3), nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    sync_status = db.Column(db.String(10), nullable=False, default="PENDING")
    created_at = db.Column(db.TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.TIMESTAMP(timezone=True), nullable=True, onupdate=datetime.utcnow
    )

    combo = db.relationship("ProductCombo", back_populates="items", lazy=True)
    product = db.relationship("Product", lazy=True, foreign_keys=[product_uid_fk])

    def to_dict(self):
        return {
            "uid": self.uid,
            "combo_uid_fk": self.combo_uid_fk,
            "product_uid_fk": self.product_uid_fk,
            "description": self.product.description if self.product else "",
            "quantity": float(self.quantity) if self.quantity is not None else 0.0,
            "unit_price": float(self.unit_price) if self.unit_price is not None else 0.0,
            "sync_status": self.sync_status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @staticmethod
    def from_json(data):
        return ProductComboItem(
            uid=data.get("uid"),
            combo_uid_fk=data.get("combo_uid_fk"),
            product_uid_fk=data.get("product_uid_fk"),
            quantity=data.get("quantity", 0),
            unit_price=data.get("unit_price", 0),
            sync_status=data.get("sync_status", "PENDING"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
