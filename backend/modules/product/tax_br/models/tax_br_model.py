from backend.apps.commerciall_api.main import db

class TaxBr(db.Model):
    __bind_key__ = 'DB_MAIN'  # SQLAlchemy to use the 'product' bind
    __tablename__ = "product_tax_br"

    uid = db.Column(db.String, primary_key=True)
    organization_uid_fk = db.Column(db.String, nullable=False)
    product_uid_fk = db.Column(db.String, db.ForeignKey("produtos.produtos_id"), nullable=False)
    ncm = db.Column(db.String(10), nullable=True)
    cst = db.Column(db.String(8), nullable=True)
    icms_pis_cofins_group_uid_fk = db.Column(db.String(36), nullable=True)
    ibs_cbs_uid_fk = db.Column(db.String(36), nullable=True)
    cred_presumido = db.Column(db.Integer, nullable=True)
    sync_status = db.Column(db.String(10), nullable=True, default="PENDING")
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=True)

    product = db.relationship("Product", back_populates="product_tax_br", lazy=True)

    def to_dict(self):
        return {
            "uid": self.uid,
            "organization_uid_fk": self.organization_uid_fk,
            "product_uid_fk": self.product_uid_fk,
            "ncm": self.ncm,
            "cst": self.cst,
            "icms_pis_cofins_group_uid_fk": self.icms_pis_cofins_group_uid_fk,
            "ibs_cbs_uid_fk": self.ibs_cbs_uid_fk,
            "cred_presumido": self.cred_presumido,
            "sync_status": self.sync_status,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @staticmethod
    def from_json(data):
        return TaxBr(
            uid=data.get("uid"),
            organization_uid_fk=data.get("organization_uid_fk"),
            product_uid_fk=data.get("product_uid_fk"),
            ncm=data.get("ncm"),
            cst=data.get("cst"),
            icms_pis_cofins_group_uid_fk=data.get("icms_pis_cofins_group_uid_fk"),
            ibs_cbs_uid_fk=data.get("ibs_cbs_uid_fk"),
            cred_presumido=data.get("cred_presumido"),
            sync_status=data.get("sync_status"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )

