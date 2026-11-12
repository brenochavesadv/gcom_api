from datetime import datetime
from backend.apps.commerciall_api.main import db

class ProductCategory(db.Model):
    __bind_key__ = 'DB_MAIN'  # SQLAlchemy to use the 'product' bind
    __tablename__ = "product_category"

    uid = db.Column(db.String(36), primary_key=True)
    main_organization_uid_fk = db.Column(db.String(36), nullable=False)
    parent_uid = db.Column(db.String(36), db.ForeignKey("product_category.uid"), nullable=True)
    pt_br = db.Column(db.String(25), nullable=True)
    sync_status = db.Column(db.String(10), nullable=True, default="PENDING")
    created_at = db.Column(db.TIMESTAMP(timezone=True), default=datetime.now)
    updated_at = db.Column(db.TIMESTAMP(timezone=True), default=datetime.now, onupdate=datetime.now)

    product = db.relationship("Product", back_populates="product_category", lazy=True)


    def to_dict(self):
        return {
            "uid": self.uid,
            "main_organization_uid_fk": self.main_organization_uid_fk,
            "parent_uid": self.parent_uid,
            "pt_br": self.pt_br,
            "sync_status": self.sync_status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    # FACTORY FOR PROD_CATEGORY_MODEL:
    def from_json(data):
            uid=data.get("uid")
            main_organization_uid_fk=data.get("main_organization_uid_fk")
            parent_uid=data.get("parent_uid")
            pt_br=data.get("pt_br")
            sync_status=data.get("sync_status", "PENDING")
            created_at=data.get("created_at")
            updated_at=data.get("updated_at") 

            return ProductCategory(
                uid= uid if uid is not None else "",
                main_organization_uid_fk=main_organization_uid_fk,
                parent_uid=parent_uid if parent_uid is not None else "",
                pt_br=pt_br,
                sync_status=sync_status,
                created_at=created_at,
                updated_at=updated_at
            )
        