from datetime import datetime

from backend.apps.commerciall_api.main import db


class ProductCombo(db.Model):
    """Persisted combo header for one shared product and organization."""

    __bind_key__ = "DB_MAIN"
    __tablename__ = "product_combo"

    uid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_uid_fk = db.Column(
        db.Integer,
        db.ForeignKey("produtos.produtos_id"),
        nullable=False,
    )
    organization_uid_fk = db.Column(db.Integer, nullable=False)
    sync_status = db.Column(db.String(10), nullable=False, default="PENDING")
    created_at = db.Column(db.TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.TIMESTAMP(timezone=True), nullable=True, onupdate=datetime.utcnow
    )
    __table_args__ = (
        db.UniqueConstraint(
            "product_uid_fk", "organization_uid_fk", name="uq_product_combo_scope"
        ),
    )

    product = db.relationship("Product", back_populates="product_combo", lazy=True)
    items = db.relationship(
        "ProductComboItem",
        back_populates="combo",
        cascade="all, delete-orphan",
        order_by="ProductComboItem.uid",
        lazy=True,
    )

    def to_dict(self):
        return {
            "uid": self.uid,
            "product_uid_fk": self.product_uid_fk,
            "organization_uid_fk": self.organization_uid_fk,
            "sync_status": self.sync_status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "combo_items": [item.to_dict() for item in self.items],
        }

    @staticmethod
    def from_json(data):
        return ProductCombo(
            uid=data.get("uid"),
            product_uid_fk=data.get("product_uid_fk"),
            organization_uid_fk=data.get("organization_uid_fk"),
            sync_status=data.get("sync_status", "PENDING"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
