from datetime import datetime
from backend.apps.commerciall_api.main import db

class ProductCfg (db.Model):
    __bind_key__ = 'DB_MAIN'
    __tablename__ = "product_cfg"
    
    organization_uid_fk = db.Column(db.String(36), nullable=False, primary_key=True)
    allow_change_price_during_sale = db.Column(db.Integer, nullable=False, default=1, comment="1=allow 0=not allow")
    default_profit = db.Column(db.Float, nullable=True)
    title_price_1 = db.Column(db.String(20), nullable=True)
    title_price_2 = db.Column(db.String(20), nullable=True)
    title_price_3 = db.Column(db.String(20), nullable=True)
    title_price_4 = db.Column(db.String(20), nullable=True)
    title_price_5 = db.Column(db.String(20), nullable=True)
    type_percent_over_price_1 = db.Column(db.Integer, nullable=False, default=1, comment="1=addition ou 2=discount")
    percent_to_price_2 = db.Column(db.Float, nullable=True)
    percent_to_price_3 = db.Column(db.Float, nullable=True)
    percent_to_price_4 = db.Column(db.Float, nullable=True)
    percent_to_price_5 = db.Column(db.Float, nullable=True)
    commission_over_price_1 = db.Column(db.Float, nullable=True)
    commission_over_price_2 = db.Column(db.Float, nullable=True)
    commission_over_price_3 = db.Column(db.Float, nullable=True)
    commission_over_price_4 = db.Column(db.Float, nullable=True)
    commission_over_price_5 = db.Column(db.Float, nullable=True)
    max_discount_over_price_1 = db.Column(db.Float, nullable=True)
    max_discount_over_price_2 = db.Column(db.Float, nullable=True)
    max_discount_over_price_3 = db.Column(db.Float, nullable=True)
    max_discount_over_price_4 = db.Column(db.Float, nullable=True)
    max_discount_over_price_5 = db.Column(db.Float, nullable=True)
    sync_status = db.Column(db.String(10), nullable=False, default="PENDING")
    updated_at = db.Column(db.TIMESTAMP(timezone=True), nullable=True, onupdate=db.func.now())

    def to_dict(self):
        return {
            "organization_uid_fk": self.organization_uid_fk,
            "allow_change_price_during_sale": self.allow_change_price_during_sale,
            "default_profit": self.default_profit,
            "title_price_1": self.title_price_1,
            "title_price_2": self.title_price_2,
            "title_price_3": self.title_price_3,
            "title_price_4": self.title_price_4,
            "title_price_5": self.title_price_5,
            "type_percent_over_price_1": self.type_percent_over_price_1,
            "percent_to_price_2": self.percent_to_price_2,
            "percent_to_price_3": self.percent_to_price_3,
            "percent_to_price_4": self.percent_to_price_4,
            "percent_to_price_5": self.percent_to_price_5,
            "commission_over_price_1": self.commission_over_price_1,
            "commission_over_price_2": self.commission_over_price_2,
            "commission_over_price_3": self.commission_over_price_3,
            "commission_over_price_4": self.commission_over_price_4,
            "commission_over_price_5": self.commission_over_price_5,
            "max_discount_over_price_1": self.max_discount_over_price_1,
            "max_discount_over_price_2": self.max_discount_over_price_2,
            "max_discount_over_price_3": self.max_discount_over_price_3,
            "max_discount_over_price_4": self.max_discount_over_price_4,
            "max_discount_over_price_5": self.max_discount_over_price_5,
            "sync_status": self.sync_status,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @staticmethod
    def from_json(data):
        return ProductCfg(
            organization_uid_fk=data.get("organization_uid_fk"),
            allow_change_price_during_sale=data.get("allow_change_price_during_sale"),
            default_profit=data.get("default_profit"),
            title_price_1=data.get("title_price_1"),
            title_price_2=data.get("title_price_2"),
            title_price_3=data.get("title_price_3"),
            title_price_4=data.get("title_price_4"),
            title_price_5=data.get("title_price_5"),
            type_percent_over_price_1=data.get("type_percent_over_price_1"),
            percent_to_price_2=data.get("percent_to_price_2"),
            percent_to_price_3=data.get("percent_to_price_3"),
            percent_to_price_4=data.get("percent_to_price_4"),
            percent_to_price_5=data.get("percent_to_price_5"),
            commission_over_price_1=data.get("commission_over_price_1"),
            commission_over_price_2=data.get("commission_over_price_2"),
            commission_over_price_3=data.get("commission_over_price_3"),
            commission_over_price_4=data.get("commission_over_price_4"),
            commission_over_price_5=data.get("commission_over_price_5"),
            max_discount_over_price_1=data.get("max_discount_over_price_1"),
            max_discount_over_price_2=data.get("max_discount_over_price_2"),
            max_discount_over_price_3=data.get("max_discount_over_price_3"),
            max_discount_over_price_4=data.get("max_discount_over_price_4"),
            max_discount_over_price_5=data.get("max_discount_over_price_5"),
            sync_status=data.get("sync_status", "PENDING"),
            updated_at=datetime.fromisoformat(data["updated_at"])
            if data.get("updated_at")
            else None,
        )


# Backward-compatible module-level entry point for older route imports.
def from_json(data):
    return ProductCfg.from_json(data)
