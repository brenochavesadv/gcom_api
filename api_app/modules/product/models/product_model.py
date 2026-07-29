from main import db
from sqlalchemy.orm import relationship

from api_app.modules.product.models.product_brand_model import ProductBrand
from api_app.modules.product.models.product_category_model import ProductCategory
from api_app.modules.product.models.product_count_model import ProductCount
from api_app.modules.product.models.product_detail_model import ProductDetail
from api_app.modules.product.models.product_expiry_model import ProductExpiry
from api_app.modules.product.models.product_supplier_model import ProductSupplier
from api_app.modules.product.models.product_tax_info_br_model import ProductTaxInfoBr
from api_app.modules.product.models.product_unit_model import ProductUnit

class Product(db.Model):
    __bind_key__ = 'DB_MAIN'
    __tablename__ = "produtos"

    uid = db.Column("produtos_id", db.Integer, primary_key=True, autoincrement=True)
    main_organization_uid_fk = db.Column("instit_matriz_id_fk", db.Integer, nullable=False, default=0)
    is_active = db.Column("ativo", db.Integer, nullable=True, default=1)
    internal_code = db.Column("codprod", db.Integer, nullable=False, default=0)
    barcode = db.Column("codbarra", db.String(25), nullable=True)
    description = db.Column("descr", db.String(60), nullable=False, default='')
    short_description = db.Column("descres", db.String(150), nullable=True)
    unit_uid_fk = db.Column("und", db.Integer, db.ForeignKey("unidades.unidades_id"), nullable=False, default=1)
    product_category_uid_fk = db.Column("prod_grp_id_fk", db.Integer, db.ForeignKey("product_category.uid"), nullable=False, default=1)
    product_category_lv1_uid = db.Column("prod_grp_nv1id", db.Integer, nullable=True, default=0)
    product_category_lv2_uid = db.Column("prod_grp_nv2id", db.Integer, nullable=False, default=0)
    size = db.Column("tam", db.Numeric(6, 3), nullable=False, default=0.000)
    width = db.Column("larg", db.Numeric(6, 3), nullable=False, default=0.000)
    height = db.Column("alt", db.Numeric(6, 3), nullable=False, default=0.000)
    cubage = db.Column("cubag", db.Numeric(7, 4), nullable=False, default=0.0000)
    weight = db.Column("peso", db.Numeric(10, 2), nullable=True)
    product_brand_uid_fk = db.Column("fabr_id_fk", db.Integer, db.ForeignKey("fabpro.fabpro_id"), nullable=False, default=1)
    supplier_person_uid_fk = db.Column("forn_pescod_id_fk", db.Integer, nullable=True, default=1, comment="Selected supplier person code")
    additional_info = db.Column("caract", db.String(200), nullable=True)
    ncm = db.Column("ncm", db.String(8), nullable=True)
    cest = db.Column("cest", db.String(8), nullable=True)
    desnf = db.Column("desnf", db.String(40), nullable=False, default='informe a descricao trib do produto')
    is_combo = db.Column("combo", db.Integer, nullable=False, default=0)
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

    product_brand = relationship(ProductBrand, back_populates="products", lazy="joined")
    product_detail = relationship("ProductDetail", back_populates="products", lazy="joined")
    product_expiry = relationship("ProductExpiry", back_populates="products", lazy="joined")
    product_count = relationship("ProductCount", back_populates="products", lazy="joined")
    product_category = relationship("ProductCategory", back_populates="products", lazy="joined")
    product_supplier = relationship("ProductSupplier", back_populates="products", lazy="joined")
    product_unit = relationship("ProductUnit", lazy="joined")
    product_tax_info = relationship("ProductTaxInfoBr", back_populates="products", lazy="joined")

    def to_dict(self):
        return {
            "uid": self.uid,
            "main_organization_uid_fk": self.main_organization_uid_fk,
            "is_active": self.is_active,
            "internal_code": self.internal_code,
            "barcode": self.barcode,
            "description": self.description,
            "short_description": self.short_description,
            "unit_uid_fk": self.unit_uid_fk,
            "product_category_uid_fk": self.product_category_uid_fk,
            "product_category_lv1_uid": self.product_category_lv1_uid,
            "product_category_lv2_uid": self.product_category_lv2_uid,
            "size": self.size,
            "width": self.width,
            "height": self.height,
            "cubage": self.cubage,
            "weight": self.weight,
            "product_brand_uid_fk": self.product_brand_uid_fk,
            "supplier_person_uid_fk": self.supplier_person_uid_fk,
            "additional_info": self.additional_info,
            "ncm": self.ncm,
            "cest": self.cest,
            "desnf": self.desnf,
            "is_combo": self.is_combo,
            "image": self.image,
            "image_bytes": self.image_bytes,
            "sync_status": self.sync_status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "product_brand": self.product_brand.to_dict() if self.product_brand else None,
            "product_detail": self.product_detail.to_dict() if self.product_detail else None,
            "product_expiry": self.product_expiry.to_dict() if self.product_expiry else None,
            "product_count": self.product_count.to_dict() if self.product_count else None,
            "product_category": self.product_category.to_dict() if self.product_category else None,
            "product_supplier": self.product_supplier.to_dict() if self.product_supplier else None,
            "product_unit": self.product_unit.to_dict() if self.product_unit else None,
            "product_tax_info": self.product_tax_info.to_dict() if self.product_tax_info else None
        }

    @staticmethod
    def from_json(**kwargs):
        return Product(
            uid=kwargs.get("uid"),
            main_organization_uid_fk=kwargs.get("main_organization_uid_fk"),
            is_active=kwargs.get("is_active"),
            internal_code=kwargs.get("internal_code"),
            barcode=kwargs.get("barcode"),
            description=kwargs.get("description"),
            short_description=kwargs.get("short_description"),
            unit_uid_fk=kwargs.get("unit_uid_fk"),
            product_category_uid_fk=kwargs.get("product_category_uid_fk"),
            product_category_lv1_uid=kwargs.get("product_category_lv1_uid"),
            product_category_lv2_uid=kwargs.get("product_category_lv2_uid"),
            size=kwargs.get("size"),
            width=kwargs.get("width"),
            height=kwargs.get("height"),
            cubage=kwargs.get("cubage"),
            weight=kwargs.get("weight"),
            product_brand_uid_fk=kwargs.get("product_brand_uid_fk"),
            supplier_person_uid_fk=kwargs.get("supplier_person_uid_fk"),
            additional_info=kwargs.get("additional_info"),
            ncm=kwargs.get("ncm"),
            cest=kwargs.get("cest"),
            desnf=kwargs.get("desnf"),
            is_combo=kwargs.get("is_combo"),
            image=kwargs.get("image"),
            image_bytes=kwargs.get("image_bytes"),
            sync_status=kwargs.get("sync_status", "PENDING"),
            created_at=kwargs.get("created_at"),
            updated_at=kwargs.get("updated_at")
        )
