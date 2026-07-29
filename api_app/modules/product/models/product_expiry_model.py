from datetime import datetime
from main import db
from sqlalchemy.orm import relationship

class ProductExpiry(db.Model):
    __bind_key__ = 'DB_MAIN'  # SQLAlchemy to use the 'product' bind
    __tablename__ = "product_expiry"

    uid = db.Column(db.String(14), primary_key=True)
    product_uid_fk = db.Column(db.Integer, db.ForeignKey("produtos.produtos_id"), nullable=False)
    organization_uid_fk = db.Column(db.Integer, nullable=False)
    expiration_date = db.Column(db.Date, nullable=True)
    sync_status = db.Column("sync_status", db.String(10), nullable=True, default="PENDING")
    created_at = db.Column(db.TIMESTAMP(timezone=True), nullable=False, default=datetime.now)

    products = db.relationship("Product", back_populates="product_expiry", lazy=True)

    def to_dict(self):
        return {
            'uid': self.uid,
            'product_uid_fk': self.product_uid_fk,
            'organization_uid_fk': self.organization_uid_fk,
            'expiration_date': self.expiration_date,
            'sync_status': self.sync_status,
            'created_at': self.created_at,
        }
    
    def __repr__(self):
        return f"<ProductExpiry {self.uid} - {self.product_uid_fk}>"

    def __str__(self):
        return f"ProductExpiry(uid={self.uid}, product_uid_fk={self.product_uid_fk})"