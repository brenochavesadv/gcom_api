from main import db

class ProductSupplier(db.Model):
    __bind_key__ = 'DB_MAIN'  # SQLAlchemy to use the 'product' bind
    __tablename__ = "prod_forn"

    uid = db.Column("id", db.Integer, primary_key=True)
    organization_uid_fk = db.Column("matriz_id_fk", db.Integer, primary_key=False) 
    product_uid_fk = db.Column("produtos_id_fk", db.Integer, db.ForeignKey("produtos.produtos_id"), primary_key=False)  
    person_uid_fk = db.Column("pescod_id_fk", db.Integer, primary_key=False)
    product_supplier_code = db.Column("prod_cod_forn", db.String, primary_key=False, comment="Product code on supplier")
    sync_status = db.Column(db.String(10), nullable=True, default="PENDING")
    created_at = db.Column(db.TIMESTAMP(timezone=True), nullable=False, default=db.func.now())
    updated_at = db.Column(db.TIMESTAMP(timezone=True), nullable=True, onupdate=db.func.now())

    products = db.relationship("Product", back_populates="product_supplier", lazy=True)


    def to_dict(self):
        """Convert model to dictionary using direct attribute access"""
        return {
            'uid': self.uid,
            'organization_uid_fk': self.organization_uid_fk,
            'product_uid_fk': self.product_uid_fk,
            'person_uid_fk': self.person_uid_fk,
            'product_supplier_code': self.product_supplier_code,
            'sync_status': self.sync_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


def __repr__(self):
    return f"<ProductSupplier {self.uid}>"

def __str__(self):
    return self.__repr__()

@staticmethod
def from_json(**kwargs):
    return ProductSupplier(
        uid=kwargs.get("uid"),
        organization_uid_fk=kwargs.get("organization_uid_fk"),
        product_uid_fk=kwargs.get("product_uid_fk"),
        person_uid_fk=kwargs.get("person_uid_fk"),
        product_supplier_code=kwargs.get("product_supplier_code"),
        sync_status=kwargs.get("sync_status", "PENDING"),
        created_at=kwargs.get("created_at"),
        updated_at=kwargs.get("updated_at")
    )