from main import db
from datetime import datetime


class ProductTaxInfoBr(db.Model):
    __bind_key__ = 'sales'  # SQLAlchemy to use the 'product' bind
    __tablename__ = "aliquotas"

    uid = db.Column("aliquotas_id", db.Integer, primary_key=True)
    organization_uid_fk = db.Column("instit_id_fk", db.Integer, nullable=False, default=0)
    description = db.Column("descr", db.String(6), nullable=False, default="")
    bematech = db.Column("bematech", db.String(2), nullable=False, default="")
    value = db.Column("valor", db.Numeric(5, 2), nullable=True)
    updated_at = db.Column("updated_at", db.TIMESTAMP(timezone=True), default=datetime.now)

def to_dict(self):
    return {
        "uid": self.uid,
        "organization_uid_fk": self.organization_uid_fk,
        "description": self.description,
        "bematech": self.bematech,
        "value": self.value,
        "updated_at": self.updated_at
    }

def __repr__(self):
    return f"<ProductTaxInfoBr {self.uid} - {self.organization_uid_fk}>"

def __str__(self):
    return f"ProductTaxInfoBr(uid={self.uid}, organization_uid_fk={self.organization_uid_fk})"

# factory

def create(**kwargs):
    return ProductTaxInfoBr(
        organization_uid_fk=kwargs.get("organization_uid_fk", 0),
        description=kwargs.get("description", ""),
        bematech=kwargs.get("bematech", ""),
        value=kwargs.get("value", 0),
        updated_at=datetime.now()
    )

