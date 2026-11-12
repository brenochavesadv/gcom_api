from backend.modules.product.tax_br.models.icms_pis_cofins_item_model import IcmsPisCofinsItem
from backend.apps.commerciall_api.main import db

class IcmsPisCofinsGroup(db.Model):
    __tablename__ = 'product_tax_br_icms_pis_cofins_group'

    uid = db.Column(db.String(36), primary_key=True)
    organization_uid_fk = db.Column(db.String(36), nullable=False)
    description = db.Column(db.String(60), nullable=False)
    cfop_sell_same_uf_item_uid_fk = db.Column(db.String(36), nullable=False)
    cfop_sell_other_uf_item_uid_fk = db.Column(db.String(36), nullable=False)
    cfop_sell_export_item_uid_fk = db.Column(db.String(36), nullable=False)
    cfop_buy_same_uf_item_uid_fk = db.Column(db.String(36), nullable=False)
    cfop_buy_other_uf_item_uid_fk = db.Column(db.String(36), nullable=False)
    cfop_buy_import_item_uid_fk = db.Column(db.String(36), nullable=False)
    sync_status = db.Column(db.String(10), nullable=False, default="PENDING")
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)

    items = db.relationship('IcmsPisCofinsItem', backref='group', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "uid": self.uid,
            "organization_uid_fk": self.organization_uid_fk,
            "description": self.description,
            "cfop_sell_same_uf_item_uid_fk": self.cfop_sell_same_uf_item_uid_fk,
            "cfop_sell_other_uf_item_uid_fk": self.cfop_sell_other_uf_item_uid_fk,
            "cfop_sell_export_item_uid_fk": self.cfop_sell_export_item_uid_fk,
            "cfop_buy_same_uf_item_uid_fk": self.cfop_buy_same_uf_item_uid_fk,
            "cfop_buy_other_uf_item_uid_fk": self.cfop_buy_other_uf_item_uid_fk,
            "cfop_buy_import_item_uid_fk": self.cfop_buy_import_item_uid_fk,
            "sync_status": self.sync_status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "items": [item.to_dict() for item in self.items],
        }
