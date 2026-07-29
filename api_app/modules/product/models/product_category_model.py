from datetime import datetime
from main import db

class ProductCategory(db.Model):
    __bind_key__ = 'DB_MAIN'  # SQLAlchemy to use the 'product' bind
    __tablename__ = "product_category"

    uid = db.Column(db.String(36), primary_key=True)
    main_organization_uid_fk = db.Column(db.String(36), nullable=False)
    parent_uid = db.Column(db.String(36), db.ForeignKey("product_category.uid"), nullable=True)
    path = db.Column(db.String(255), nullable=True)
    pt_br = db.Column(db.String(25), nullable=True)
    sync_status = db.Column(db.String(10), nullable=True, default="PENDING")
    created_at = db.Column(db.TIMESTAMP(timezone=True), default=datetime.now)
    updated_at = db.Column(db.TIMESTAMP(timezone=True), default=datetime.now, onupdate=datetime.now)

    products = db.relationship("Product", back_populates="product_category", lazy=True)


    def to_dict(self):
        """Convert model to dictionary using direct attribute access"""
        return {
            'uid': self.uid,
            'main_organization_uid_fk': self.main_organization_uid_fk,
            'parent_uid': self.parent_uid,
            'path': self.path,
            'pt_br': self.pt_br,
            'sync_status': self.sync_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f"<ProdCategory {self.uid} - {self.main_organization_uid_fk}>"

    def __str__(self):
        return f"ProdCategory(uid={self.uid}, main_organization_uid_fk={self.main_organization_uid_fk})"

    # FACTORY FOR PROD_CATEGORY_MODEL:
    def from_json(**kwargs):
        return ProductCategory(
            uid=kwargs.get("uid"),
            main_organization_uid_fk=kwargs.get("main_organization_uid_fk"),
            parent_uid=kwargs.get("parent_uid"),
            path=kwargs.get("path"),
            pt_br=kwargs.get("pt_br"),
            sync_status=kwargs.get("sync_status", "PENDING"),
            created_at=kwargs.get("created_at") or datetime.now(),
            updated_at=kwargs.get("updated_at") or datetime.now()
        )