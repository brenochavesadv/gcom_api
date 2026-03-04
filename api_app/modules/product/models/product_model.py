from main import db
from datetime import datetime
from sqlalchemy.orm import relationship

class Product(db.Model):
    __tablename__ = "produtos"

    product_uid = db.Column("produtos_id", db.Integer, primary_key=True, autoincrement=True)
    organization_uid_fk = db.Column("instit_matriz_id_fk", db.Integer, nullable=False, default=0)
    is_active = db.Column("ativo", db.Integer, nullable=True, default=1)
    internal_code = db.Column("codprod", db.Integer, nullable=False, default=0)
    barcode = db.Column("codbarra", db.String(25), nullable=True)
    description = db.Column("descr", db.String(60), nullable=False, default='')
    especification = db.Column("descres", db.String(150), nullable=True)
    # Replace FK with plain Integer if unidades is in another database
    # unit_uid_fk = db.Column("und", db.Integer, db.ForeignKey('unidades.unidades_id'), nullable=False, default=1)
    unit_uid_fk = db.Column("und", db.Integer, nullable=False, default=1)
    product_group_uid_fk = db.Column("prod_grp_id_fk", db.Integer, nullable=False, default=1)
    product_group_lv1_uid = db.Column("prod_grp_nv1id", db.Integer, nullable=True, default=0)
    product_group_lv2_uid = db.Column("prod_grp_nv2id", db.Integer, nullable=False, default=0)
    size = db.Column("tam", db.Numeric(6, 3), nullable=False, default=0.000)
    width = db.Column("larg", db.Numeric(6, 3), nullable=False, default=0.000)
    height = db.Column("alt", db.Numeric(6, 3), nullable=False, default=0.000)
    cubage = db.Column("cubag", db.Numeric(7, 4), nullable=False, default=0.0000)
    weight = db.Column("peso", db.Numeric(10, 2), nullable=True)
    product_brand_uid_fk = db.Column("fabr_id_fk", db.Integer, nullable=False, default=1)
    person_uid_fk = db.Column("forn_pescod_id_fk", db.Integer, nullable=True, default=1)
    additional_info = db.Column("caract", db.String(200), nullable=True)
    ncm = db.Column("ncm", db.String(8), nullable=True)
    cest = db.Column("cest", db.String(8), nullable=True)
    desnf = db.Column("desnf", db.String(40), nullable=False, default='informe a descricao trib do produto')
    combo = db.Column("combo", db.Integer, nullable=False, default=0)
    image = db.Column("foto", db.String(25), nullable=False, default='nofoto.gif')
    image_bytes = db.Column("img_bites", db.Integer, nullable=True, default=8878)
    updated_at = db.Column("datatz", db.TIMESTAMP(timezone=True), nullable=True)

    __table_args__ = (
        db.UniqueConstraint('instit_matriz_id_fk', 'codprod', name='codprod'),
        db.UniqueConstraint('instit_matriz_id_fk', 'descr', name='descr'),
        db.UniqueConstraint('instit_matriz_id_fk', 'codbarra', name='codbarra'),
    )

    product_expiry = relationship("ProductExpiry", back_populates="product", uselist=False)

    def to_dict(self):
        return {
            "product_uid": self.product_uid,
            "organization_uid_fk": self.organization_uid_fk,
            "is_active": True if self.is_active == 2 else False,
            "internal_code": self.internal_code,
            "barcode": self.barcode,
            "description": self.description,
            "short_description": self.short_description,
            "unit_uid_fk": self.unit_uid_fk,
            "product_group_uid_fk": self.product_group_uid_fk,
            "product_group_lv1_uid": self.product_group_lv1_uid,
            "product_group_lv2_uid": self.product_group_lv2_uid,
            "size": float(self.size) if self.size else 0,
            "width": float(self.width) if self.width else 0,
            "height": float(self.height) if self.height else 0,
            "cubage": float(self.cubage) if self.cubage else 0,
            "weight": float(self.weight) if self.weight else 0,
            "product_brand_uid_fk": self.product_brand_uid_fk,
            "person_uid_fk": self.person_uid_fk,
            "characteristics": self.characteristics,
            "ncm": self.ncm,
            "cest": self.cest,
            "desnf": self.desnf,
            "combo": self.combo,
            "image": self.image,
            "image_bytes": self.image_bytes,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    @staticmethod
    def create(**kw):
        return Product(
            product_uid=kw.get("product_uid"),
            organization_uid_fk=kw.get("organization_uid_fk"),
            is_active=kw.get("is_active"),
            internal_code=kw.get("internal_code"),
            barcode=kw.get("barcode"),
            description=kw.get("description"),
            short_description=kw.get("short_description"),
            unit_uid_fk=kw.get("unit_uid_fk"),
            product_group_uid_fk=kw.get("product_group_uid_fk"),
            product_group_lv1_uid=kw.get("product_group_lv1_uid"),
            product_group_lv2_uid=kw.get("product_group_lv2_uid"),
            size=kw.get("size"),
            width=kw.get("width"),
            height=kw.get("height"),
            cubage=kw.get("cubage"),
            weight=kw.get("weight"),
            product_brand_uid_fk=kw.get("product_brand_uid_fk"),
            person_uid_fk=kw.get("person_uid_fk"),
            characteristics=kw.get("characteristics"),
            ncm=kw.get("ncm"),
            cest=kw.get("cest"),
            desnf=kw.get("desnf"),
            combo=kw.get("combo"),
            image=kw.get("image"),  
            image_bytes=kw.get("image_bytes"),
            updated_at=kw.get("updated_at")
        )
