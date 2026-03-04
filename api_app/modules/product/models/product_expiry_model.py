from datetime import datetime
from main import db
from sqlalchemy.orm import relationship

class ProductExpiry(db.Model):
    __bind_key__ = 'sales'  # SQLAlchemy to use the 'product' bind
    __tablename__ = "product_expiry"

    uid = db.Column(db.String(14), primary_key=True)
    product_uid_fk = db.Column(db.Integer, nullable=False)
    organization_uid_fk = db.Column(db.Integer, nullable=False)
    expiry_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.TIMESTAMP(timezone=True), nullable=False, default=datetime.now)
    updated_at = db.Column(db.TIMESTAMP(timezone=True), nullable=True, onupdate=datetime.now)

    product = relationship("Product", back_populates="product_expiry")

    def to_dict(self):
        return {
            'uid': self.uid,
            'product_uid_fk': self.product_uid_fk,
            'organization_uid_fk': self.organization_uid_fk,
            'expiry_date': self.expiry_date,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    def __repr__(self):
        return f"<ProductExpiry {self.uid} - {self.product_uid_fk}>"

    def __str__(self):
        return f"ProductExpiry(uid={self.uid}, product_uid_fk={self.product_uid_fk})"