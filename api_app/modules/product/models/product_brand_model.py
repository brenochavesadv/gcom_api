from main import db

class ProductBrand(db.Model):
    __bind_key__ = 'DB_MAIN'  # SQLAlchemy to use the 'product' bind
    __tablename__ = "fabpro"

    uid = db.Column("fabpro_id", db.Integer, primary_key=True)
    organization_uid_fk = db.Column("instit_id_fk", db.Integer)
    factory = db.Column("fabr", db.String(40), nullable=False)
    brand = db.Column("marca", db.String(25), nullable=False)
    sync_status = db.Column("sync_status", db.String(10), nullable=True, default=0)
    created_at = db.Column("created_at", db.TIMESTAMP(timezone=True), nullable=False, default=db.func.now())
    updated_at = db.Column("updated_at", db.TIMESTAMP(timezone=True), nullable=True, onupdate=db.func.now())

    products = db.relationship("Product", back_populates="product_brand", lazy=True)
   
    def to_dict(self):
        return {
            "uid": self.uid,
            "organization_uid_fk": self.organization_uid_fk,
            "factory": self.factory,
            "brand": self.brand,
            "sync_status": self.sync_status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self):
        return f"<ProductBrand {self.uid} - {self.organization_uid_fk}>"

    def __str__(self):
        return f"ProductBrand(uid={self.uid}, organization_uid_fk={self.organization_uid_fk})"

    # factory method
    @staticmethod
    def from_json(**kwargs):
        return ProductBrand(
            organization_uid_fk=kwargs.get("organization_uid_fk"),
            factory=kwargs.get("factory"),
            brand=kwargs.get("brand"),
            sync_status=kwargs.get("sync_status", "PENDING"),
            created_at=kwargs.get("created_at"),
            updated_at=kwargs.get("updated_at")
        )