from backend.apps.commerciall_api.main import db

class IbsCbs(db.Model):
    __tablename__ = 'product_tax_br_ibs_cbs'

    uid = db.Column(db.String(36), primary_key=True)
    organization_uid_fk = db.Column(db.String(36), nullable=False)
    description = db.Column(db.String(80), nullable=False)
    cst = db.Column(db.Integer, nullable=False, default=0)
    classif_tributaria = db.Column(db.Integer, nullable=False, default=0)
    cbs_aliquota = db.Column(db.Float, nullable=False, default=0.0)
    cbs_reducao = db.Column(db.Float, nullable=False, default=0.0)
    ibs_aliquota = db.Column(db.Float, nullable=False, default=0.0)
    ibs_reducao = db.Column(db.Float, nullable=False, default=0.0)
    ibs_municip_aliquota = db.Column(db.Float, nullable=False, default=0.0)
    ibs_municip_reducao = db.Column(db.Float, nullable=False, default=0.0)
    account_section_uid_fk = db.Column(db.Integer, nullable=False, default=0)
    sync_status = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)

    @staticmethod
    def from_json(data):
        return IbsCbs(
            uid=data.get("uid"),
            organization_uid_fk=data.get("organization_uid_fk"),
            description=data.get("description"),
            cst=data.get("cst"),
            classif_tributaria=data.get("classif_tributaria"),
            cbs_aliquota=data.get("cbs_aliquota"),
            cbs_reducao=data.get("cbs_reducao"),
            ibs_aliquota=data.get("ibs_aliquota"),
            ibs_reducao=data.get("ibs_reducao"),
            ibs_municip_aliquota=data.get("ibs_municip_aliquota"),
            ibs_municip_reducao=data.get("ibs_municip_reducao"),
            account_section_uid_fk=data.get("account_section_uid_fk"),
            sync_status=data.get("sync_status"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )

    def to_dict(self):
            return {
                "uid": self.uid,
                "organization_uid_fk": self.organization_uid_fk,
                "description": self.description,
                "cst": self.cst,
                "classif_tributaria": self.classif_tributaria,
                "cbs_aliquota": self.cbs_aliquota,
                "cbs_reducao": self.cbs_reducao,
                "ibs_aliquota": self.ibs_aliquota,
                "ibs_reducao": self.ibs_reducao,
                "ibs_municip_aliquota": self.ibs_municip_aliquota,
                "ibs_municip_reducao": self.ibs_municip_reducao,
                "account_section_uid_fk": self.account_section_uid_fk,
                "sync_status": self.sync_status,
                "created_at": self.created_at,
                "updated_at": self.updated_at
            }