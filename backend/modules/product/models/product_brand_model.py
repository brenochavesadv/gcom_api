from backend.apps.commerciall_api.main import db

class ProductBrand(db.Model):
    __bind_key__ = 'DB_MAIN'  # SQLAlchemy to use the 'product' bind
    __tablename__ = "fabpro"

    uid = db.Column("fabpro_id", db.Integer, primary_key=True)
    main_organization_uid_fk = db.Column("instit_id_fk", db.Integer)
    factory = db.Column("fabr", db.String(40), nullable=False)
    brand = db.Column("marca", db.String(25), nullable=False)
    sync_status = db.Column("sync_status", db.String(10), nullable=True, default=0)
    created_at = db.Column("created_at", db.TIMESTAMP(timezone=True), nullable=False, default=db.func.now())
    updated_at = db.Column("updated_at", db.TIMESTAMP(timezone=True), nullable=True, onupdate=db.func.now())

    product = db.relationship("Product", back_populates="product_brand", lazy=True)
   
    def to_dict(self):
        return {
            "uid": self.uid,
            "main_organization_uid_fk": self.main_organization_uid_fk,
            "factory": self.factory,
            "brand": self.brand,
            "sync_status": self.sync_status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    # factory method
    @staticmethod
    def from_json(data):
        return ProductBrand(
            uid=data.get("uid"),
            main_organization_uid_fk=data.get("main_organization_uid_fk"),
            factory=data.get("factory"),
            brand=data.get("brand"),
            sync_status=data.get("sync_status", "PENDING"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )