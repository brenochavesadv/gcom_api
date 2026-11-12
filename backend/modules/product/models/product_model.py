from backend.apps.commerciall_api.main import db
from sqlalchemy.orm import relationship

from backend.modules.product.models.product_brand_model import ProductBrand
from backend.modules.product.models.product_category_model import ProductCategory
from backend.modules.product.models.product_count_model import ProductCount
from backend.modules.product.models.product_detail_model import ProductDetail
from backend.modules.product.models.product_expiry_model import ProductExpiry
from backend.modules.product.models.product_supplier_model import ProductSupplier
from backend.modules.product.tax_br.models.tax_br_model import TaxBr
from backend.modules.unit.unit_model import Unit

class Product(db.Model):
    __bind_key__ = 'DB_MAIN'
    __tablename__ = "produtos"

    uid = db.Column("produtos_id", db.Integer, primary_key=True, autoincrement=True)
    main_organization_uid_fk = db.Column("instit_matriz_id_fk", db.Integer, nullable=False, default=0)
    is_active = db.Column("ativo", db.Integer, nullable=True, default=1, comment='1 = Inactive, 2 = Active')
    internal_code = db.Column("codprod", db.Integer, nullable=False, default=0)
    barcode = db.Column("codbarra", db.String(25), nullable=True)
    description = db.Column("descr", db.String(60), nullable=False, default='')
    short_description = db.Column("descres", db.String(150), nullable=True)
    unit_id_fk = db.Column("und", db.SmallInteger, db.ForeignKey("unit.id"), nullable=False, default=1)
    product_category_uid_fk = db.Column("prod_grp_id_fk", db.Integer, db.ForeignKey("product_category.uid"), nullable=False, default=1)
    product_category_lv1_uid = db.Column("prod_grp_nv1id", db.Integer, nullable=True, default=0)
    product_category_lv2_uid = db.Column("prod_grp_nv2id", db.Integer, nullable=False, default=0)
    size = db.Column(db.String(20), nullable=True, default='')
    lenght = db.Column("tam", db.Numeric(6, 3), nullable=False, default=0.000)
    width = db.Column("larg", db.Numeric(6, 3), nullable=False, default=0.000)
    height = db.Column("alt", db.Numeric(6, 3), nullable=False, default=0.000)
    cubage = db.Column("cubag", db.Numeric(7, 4), nullable=False, default=0.0000)
    weight = db.Column("peso", db.Numeric(10, 2), nullable=True)
    product_brand_uid_fk = db.Column("fabr_id_fk", db.Integer, db.ForeignKey("fabpro.fabpro_id"), nullable=False, default=1)
    supplier_person_uid_fk = db.Column("forn_pescod_id_fk", db.Integer, nullable=True, default=1, comment="Selected supplier person code")
    additional_info = db.Column("caract", db.String(200), nullable=True)
    allow_fractional_quantity = db.Column(db.Integer, nullable=False, default=0, comment="0 = No, 1 = Yes")
    is_own_production = db.Column(db.Integer, nullable=False, default=0, comment="0 = No, 1 = Yes")
    is_combo = db.Column("combo", db.Integer, nullable=False, default=0)
    has_expiry = db.Column("has_expiry", db.Integer, nullable=False, default=0, comment="0 = No, 1 = Yes")
    image = db.Column("foto", db.String(25), nullable=False, default='nofoto.gif')
    image_bytes = db.Column("img_bites", db.Integer, nullable=True, default=8878)
    sync_status = db.Column("sync_status", db.String(10), nullable=True, default="PENDING")
    created_at = db.Column(db.TIMESTAMP(timezone=True), nullable=False, default=db.func.now())
    updated_at = db.Column(db.TIMESTAMP(timezone=True), nullable=True, onupdate=db.func.now())

    __table_args__ = (
        db.UniqueConstraint('instit_matriz_id_fk', 'codprod', name='codprod'),
        db.UniqueConstraint('instit_matriz_id_fk', 'descr', name='descr'),
        db.UniqueConstraint('instit_matriz_id_fk', 'codbarra', name='codbarra'),
    )

    product_brand = relationship(ProductBrand, back_populates="product", lazy="joined")
    product_detail = relationship(ProductDetail, back_populates="product", lazy="joined")
    product_expiry = relationship(ProductExpiry, back_populates="product", lazy="joined")
    product_count = relationship(ProductCount, back_populates="product", lazy="joined")
    product_category = relationship(ProductCategory, back_populates="product", lazy="joined")
    product_supplier = relationship(ProductSupplier, back_populates="product", lazy="joined")
    product_tax_br = relationship(TaxBr, back_populates="product", lazy="joined")
    product_unit = relationship(Unit, lazy="joined")
    product_combo = relationship(
        "ProductCombo", back_populates="product", cascade="all, delete-orphan"
    )
    #product_tax_info = relationship("ProductTaxInfoBr", back_populates="products", lazy="joined")

    def to_dict(self):
        return {
            "uid": self.uid,
            "main_organization_uid_fk": self.main_organization_uid_fk,
            "is_active": self.is_active,
            "internal_code": self.internal_code,
            "barcode": self.barcode,
            "description": self.description,
            "short_description": self.short_description,
            "unit_id_fk": self.unit_id_fk,
            "product_category_uid_fk": self.product_category_uid_fk,
            "product_category_lv1_uid": self.product_category_lv1_uid,
            "product_category_lv2_uid": self.product_category_lv2_uid,
            "size": self.size,
            "lenght": self.lenght,
            "width": self.width,
            "height": self.height,
            "cubage": self.cubage,
            "weight": self.weight,
            "product_brand_uid_fk": self.product_brand_uid_fk,
            "supplier_person_uid_fk": self.supplier_person_uid_fk,
            "additional_info": self.additional_info,
            "allow_fractional_quantity": self.allow_fractional_quantity,
            "is_own_production": self.is_own_production,
            "is_combo": self.is_combo,
            "has_expiry": self.has_expiry,
            "image": self.image,
            "image_bytes": self.image_bytes,
            "sync_status": self.sync_status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "product_brand": self.product_brand.to_dict() if self.product_brand else None,
            "product_detail": [detail.to_dict() for detail in self.product_detail] if self.product_detail else [],
            "product_expiry": [expiry.to_dict() if expiry else None for expiry in self.product_expiry] if self.product_expiry else [],
            "product_count": [count.to_dict() if count else None for count in self.product_count] if self.product_count else [],
            "product_category": self.product_category.to_dict() if self.product_category else None,
            "product_supplier": [supplier.to_dict() if supplier else None for supplier in self.product_supplier] if self.product_supplier else [],
            "product_unit": self.product_unit.to_dict() if self.product_unit else None,
            #"product_tax_info": self.product_tax_info.to_dict() if self.product_tax_info else None
        }

    @staticmethod
    def from_json(data):
        return Product(
            uid=data.get("uid"),
            main_organization_uid_fk=data.get("main_organization_uid_fk"),
            is_active=data.get("is_active"),
            internal_code=data.get("internal_code"),
            barcode=data.get("barcode"),
            description=data.get("description"),
            short_description=data.get("short_description"),
            unit_id_fk=data.get("unit_id_fk"),
            product_category_uid_fk=data.get("product_category_uid_fk"),
            product_category_lv1_uid=data.get("product_category_lv1_uid"),
            product_category_lv2_uid=data.get("product_category_lv2_uid"),
            size=data.get("size"),
            lenght=data.get("lenght"),
            width=data.get("width"),
            height=data.get("height"),
            cubage=data.get("cubage"),
            weight=data.get("weight"),
            product_brand_uid_fk=data.get("product_brand_uid_fk"),
            supplier_person_uid_fk=data.get("supplier_person_uid_fk"),
            additional_info=data.get("additional_info"),
            allow_fractional_quantity=data.get("allow_fractional_quantity"),
            is_own_production=data.get("is_own_production"),
            is_combo=data.get("is_combo"),
            has_expiry=data.get("has_expiry"),
            image=data.get("image"),
            image_bytes=data.get("image_bytes"),
            sync_status=data.get("sync_status", "PENDING"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )
