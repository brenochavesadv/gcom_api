"""Persistence models for product receipts.

The column names mirror the legacy ``recpro`` and ``it_rec`` tables.  Receipt
items deliberately keep the values entered at receipt time; cancellation must
never recalculate them from the current product detail.
"""

from datetime import datetime, timezone

from backend.apps.commerciall_api.main import db
from backend.modules.person.models.person_model import Person
from sqlalchemy.orm import foreign


class ProductReceipt(db.Model):
    __bind_key__ = "DB_MAIN"
    __tablename__ = "recpro"

    uid = db.Column("id_recpro", db.Integer, primary_key=True)
    organization_uid_fk = db.Column("instit", db.Integer, nullable=False)
    code = db.Column("cod_receb", db.Integer, nullable=False)
    supplier_uid_fk = db.Column("idpescod", db.Integer, nullable=False)
    received_date = db.Column("data", db.DateTime, nullable=False)
    total = db.Column("valor", db.Numeric(12, 2), nullable=False, default=0)
    quantity = db.Column("qtd", db.Numeric(12, 3), nullable=False, default=0)
    generate_payable = db.Column("cpg", db.Integer, nullable=False, default=0)
    order_date = db.Column("ped_data", db.DateTime, nullable=True)
    order_number = db.Column("ped_num", db.String(15), nullable=True)
    order_value = db.Column("ped_valor", db.Numeric(12, 2), nullable=True)
    invoice_date = db.Column("nf_data", db.DateTime, nullable=True)
    invoice_number = db.Column("nf_num", db.String(15), nullable=True)
    invoice_value = db.Column("nf_valor", db.Numeric(12, 2), nullable=True)
    created_at = db.Column("datatz", db.DateTime, nullable=False)
    actor_uid = db.Column("usuatz", db.String(50), nullable=True)
    status_flag = db.Column("sit", db.Integer, nullable=False, default=1)

    items = db.relationship(
        "ProductReceiptItem",
        primaryjoin=lambda: ProductReceipt.uid == foreign(ProductReceiptItem.receipt_uid_fk),
        lazy="selectin",
        viewonly=True,
    )
    supplier = db.relationship(
        Person,
        primaryjoin=lambda: foreign(ProductReceipt.supplier_uid_fk) == Person.uid,
        viewonly=True,
        lazy="joined",
    )

    @property
    def status(self):
        return "posted" if self.status_flag == 1 else "cancelled"

    @property
    def version(self):
        stamp = self.created_at or datetime.now(timezone.utc)
        return f"{self.uid}:{stamp.isoformat()}:{self.status_flag}"


class ProductReceiptItem(db.Model):
    __bind_key__ = "DB_MAIN"
    __tablename__ = "it_rec"

    uid = db.Column("id_itrec", db.Integer, primary_key=True)
    organization_uid_fk = db.Column("instit", db.Integer, nullable=False)
    receipt_uid_fk = db.Column("idrec", db.Integer, nullable=False)
    product_uid_fk = db.Column("idprod", db.Integer, nullable=False)
    fiscal_quantity = db.Column("qtd_nf", db.Numeric(12, 3), nullable=False)
    front_quantity = db.Column("qtd_frente", db.Numeric(12, 3), nullable=False)
    storage_1_quantity = db.Column("qtd_dep1", db.Numeric(12, 3), nullable=False)
    storage_2_quantity = db.Column("qtd_dep2", db.Numeric(12, 3), nullable=False)
    storage_3_quantity = db.Column("qtd_dep3", db.Numeric(12, 3), nullable=False)
    cost_price = db.Column("custo", db.Numeric(12, 2), nullable=False)
    tax_rate_uid_fk = db.Column("aliq", db.Integer, nullable=True)
    purchase_price = db.Column("compra", db.Numeric(12, 2), nullable=False)
    freight = db.Column("frete", db.Numeric(12, 2), nullable=False)
    ipi_percent = db.Column("ipi", db.Numeric(8, 2), nullable=False)
    markup = db.Column("lucro", db.Numeric(8, 2), nullable=False)
    sale_price_1 = db.Column("venda1", db.Numeric(12, 2), nullable=False)
    sale_price_2 = db.Column("venda2", db.Numeric(12, 2), nullable=False)
    sale_price_3 = db.Column("venda3", db.Numeric(12, 2), nullable=False)
    sale_price_4 = db.Column("venda4", db.Numeric(12, 2), nullable=False)
    sale_price_5 = db.Column("venda5", db.Numeric(12, 2), nullable=False)
    status_flag = db.Column("sit", db.Integer, nullable=False, default=1)
