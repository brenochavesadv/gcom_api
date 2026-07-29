from main import db
from sqlalchemy.orm import relationship

class ProductDetail(db.Model):
    __bind_key__ = 'DB_MAIN'  # Change to 'main' to match Product model
    __tablename__ = "prod_itens"

    uid = db.Column("prod_itens_id", db.Integer, primary_key=True)
    product_uid_fk = db.Column("produtos_id_fk", db.Integer, db.ForeignKey("produtos.produtos_id"), nullable=False)
    organization_uid_fk = db.Column("instit_id_fk", db.Integer, nullable=False)
    main_organization_uid_fk = db.Column("instit_matriz_id_fk", db.Integer, nullable=False)
    internal_code = db.Column("codprod", db.Integer, nullable=False)
    is_active = db.Column("ativo", db.Integer, nullable=False, default=1, comment="2 for active, 1 for inactive") 
    inventory_reduce_on_sell = db.Column("bxest", db.Integer, nullable=False, default=0, comment="1 for stock reduction, 0 for no reduction")
    inventory_lowest_qty = db.Column("est_minimo", db.Numeric(10, 3), nullable=False, default=0.000)
    inventory_tax_qty = db.Column("est_fiscal", db.Numeric(10, 3), nullable=False, default=0.000)
    inventory_front_qty = db.Column("est_frente", db.Numeric(10, 3), nullable=False, default=0.000)
    inventory_storage_1_qty = db.Column("est_dep1", db.Numeric(10, 3), nullable=False, default=0.000)
    inventory_storage_2_qty = db.Column("est_dep2", db.Numeric(10, 3), nullable=False, default=0.000)
    inventory_storage_3_qty = db.Column("est_dep3", db.Numeric(10, 3), nullable=False, default=0.000)
    purchase_price = db.Column("compra", db.Numeric(10, 2), nullable=False, default=0.00)
    shipping_price = db.Column("frete", db.Numeric(10, 2), nullable=False, default=0.00)
    ipi = db.Column("ipi", db.Numeric(5, 2), nullable=False, default=0.00)
    aliq = db.Column("aliq", db.Integer, nullable=False, default=0)
    cost_price = db.Column("custo", db.Numeric(10, 2), nullable=False, default=0.00)
    profit = db.Column("lucro", db.Numeric(5, 2), nullable=False, default=0.00)
    sell_price_1 = db.Column("prvenda1", db.Numeric(10, 2), nullable=False, default=0.00)
    sell_price_2 = db.Column("prvenda2", db.Numeric(10, 2), nullable=False, default=0.00)
    sell_price_3 = db.Column("prvenda3", db.Numeric(10, 2), nullable=False, default=0.00)
    sell_price_4 = db.Column("prvenda4", db.Numeric(10, 2), nullable=False, default=0.00)
    sell_price_5 = db.Column("prvenda5", db.Numeric(10, 2), nullable=False, default=0.00)
    is_for_rental = db.Column("locavel", db.Integer, nullable=False, default=0, comment="1 for rental, 0 for not rental")
    rental_price = db.Column("prloc", db.Numeric(10, 2), nullable=False, default=0.00)
    is_wholesale = db.Column("vdatac", db.Integer, nullable=False, default=0 , comment="1 for wholesale, 0 for not wholesale")
    wholesale_qty = db.Column("qtdatac", db.Numeric(10, 3), nullable=False, default=0.000)
    wholesale_price = db.Column("pratac", db.Numeric(10, 2), nullable=False, default=0.00)
    inventory_front_localization = db.Column("loc_frente", db.String(50), nullable=True)
    inventory_storage_1_localization = db.Column("loc_dep1", db.String(50), nullable=True)
    inventory_storage_2_localization = db.Column("loc_dep2", db.String(50), nullable=True)
    inventory_storage_3_localization = db.Column("loc_dep3", db.String(50), nullable=True)
    seller_commission_percentage = db.Column("comissao_atv", db.Integer, nullable=False, default=0) # alterar na tabela para aceitar decimal qdo estiver em produção
    seller_commission_value = db.Column("comissao_val", db.Numeric(5, 2), nullable=False, default=0.00)
    combo_product_uid = db.Column("produtos_id_combo", db.Integer, nullable=True)
    combo_qty = db.Column("qtd_combo", db.Numeric(10, 3), nullable=False, default=0.000)
    sync_status = db.Column("sync_status", db.String(10), nullable=True, default="PENDING")
    created_at = db.Column("created_at", db.TIMESTAMP(timezone=True), nullable=False, default=db.func.now())
    updated_at = db.Column("updated_at", db.TIMESTAMP(timezone=True), nullable=True, onupdate=db.func.now())

    products = db.relationship("Product", back_populates="product_detail", lazy=True)


    def to_dict(self):  
        """Convert model to dictionary using direct attribute access"""
        return {
            'uid': self.uid,
            'product_uid_fk': self.product_uid_fk,
            'organization_uid_fk': self.organization_uid_fk,
            'main_organization_uid_fk': self.main_organization_uid_fk,
            'internal_code': self.internal_code,
            'is_active': self.is_active,
            'inventory_reduce_on_sell': self.inventory_reduce_on_sell,
            'inventory_lowest_qty': str(self.inventory_lowest_qty) if self.inventory_lowest_qty is not None else "0.000",
            'inventory_tax_qty': str(self.inventory_tax_qty) if self.inventory_tax_qty is not None else "0.000",
            'inventory_front_qty': str(self.inventory_front_qty) if self.inventory_front_qty is not None else "0.000",
            'inventory_storage_1_qty': str(self.inventory_storage_1_qty) if self.inventory_storage_1_qty is not None else "0.000",
            'inventory_storage_2_qty': str(self.inventory_storage_2_qty) if self.inventory_storage_2_qty is not None else "0.000",
            'inventory_storage_3_qty': str(self.inventory_storage_3_qty) if self.inventory_storage_3_qty is not None else "0.000",
            'purchase_price': str(self.purchase_price) if self.purchase_price is not None else "0.000",
            'shipping_price': str(self.shipping_price) if self.shipping_price is not None else "0.000",
            'ipi': str(self.ipi) if self.ipi is not None else "0.000",
            'aliq': self.aliq,
            'cost_price': str(self.cost_price) if self.cost_price is not None else "0.000",
            'profit': str(self.profit) if self.profit is not None else "0.000",
            'sell_price_1': str(self.sell_price_1) if self.sell_price_1 is not None else "0.000",
            'sell_price_2': str(self.sell_price_2) if self.sell_price_2 is not None else "0.000",
            'sell_price_3': str(self.sell_price_3) if self.sell_price_3 is not None else "0.000",
            'sell_price_4': str(self.sell_price_4) if self.sell_price_4 is not None else "0.000",
            'sell_price_5': str(self.sell_price_5) if self.sell_price_5 is not None else "0.000",
            'is_for_rental': self.is_for_rental,
            'rental_price': str(self.rental_price) if self.rental_price is not None else "0.000",
            'is_wholesale': self.is_wholesale,
            'wholesale_qty': str(self.wholesale_qty) if self.wholesale_qty is not None else "0.000",
            'wholesale_price': str(self.wholesale_price) if self.wholesale_price is not None else "0.000",
            'inventory_front_localization': self.inventory_front_localization,
            'inventory_storage_1_localization': self.inventory_storage_1_localization,
            'inventory_storage_2_localization': self.inventory_storage_2_localization,
            'inventory_storage_3_localization': self.inventory_storage_3_localization,
            'seller_commission_percentage': self.seller_commission_percentage,
            'seller_commission_value': str(self.seller_commission_value) if self.seller_commission_value is not None else "0.000",
            'combo_product_id': self.combo_product_uid,
            'combo_qty': str(self.combo_qty) if self.combo_qty is not None else "0.000",
            'sync_status': self.sync_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):  # FIX: Indent inside the class
        return f"<ProductDetail {self.uid}>"

    def __str__(self):  # FIX: Indent inside the class
        return self.__repr__()

    @staticmethod  
    def from_json(**kwargs):
        return ProductDetail(
            product_uid_fk=kwargs.get("product_uid_fk"),
            organization_uid_fk=kwargs.get("organization_uid_fk"),
            main_organization_uid_fk=kwargs.get("main_organization_uid_fk"),
            internal_code=kwargs.get("internal_code"),
            is_active=kwargs.get("is_active", 1),
            inventory_reduce_on_sell=kwargs.get("inventory_reduce_on_sell", 0),
            inventory_lowest_qty=kwargs.get("inventory_lowest_qty", 0.000),
            inventory_tax_qty=kwargs.get("inventory_tax_qty", 0.000),
            inventory_front_qty=kwargs.get("inventory_front_qty", 0.000),
            inventory_storage_1_qty=kwargs.get("inventory_storage_1_qty", 0.000),
            inventory_storage_2_qty=kwargs.get("inventory_storage_2_qty", 0.000),
            inventory_storage_3_qty=kwargs.get("inventory_storage_3_qty", 0.000),
            purchase_price=kwargs.get("purchase_price", 0.00),
            shipping_price=kwargs.get("shipping_price", 0.00),
            ipi=kwargs.get("ipi", 0.00),
            aliq=kwargs.get("aliq", 0),
            cost_price=kwargs.get("cost_price", 0.00),
            profit=kwargs.get("profit", 0.00),
            sell_price_1=kwargs.get("sell_price_1", 0.00),
            sell_price_2=kwargs.get("sell_price_2", 0.00),
            sell_price_3=kwargs.get("sell_price_3", 0.00),
            sell_price_4=kwargs.get("sell_price_4", 0.00),
            sell_price_5=kwargs.get("sell_price_5", 0.00),
            is_for_rental=kwargs.get("is_for_rental", 0),
            rental_price=kwargs.get("rental_price", 0.00),
            is_wholesale=kwargs.get("is_wholesale", 0),
            wholesale_qty=kwargs.get("wholesale_qty", 0.000),
            wholesale_price=kwargs.get("wholesale_price", 0.00),
            localization_front=kwargs.get("localization_front"),
            localization_storage_1=kwargs.get("localization_storage_1"),
            localization_storage_2=kwargs.get("localization_storage_2"),
            localization_storage_3=kwargs.get("localization_storage_3"),
            _seller_commission_percentage=kwargs.get("_seller_commission_percentage", 0),
            seller_commission_value=kwargs.get("seller_commission_value", 0.00),
            combo_product_id=kwargs.get("combo_product_id"),
            combo_qty=kwargs.get("combo_qty", 0.000),
            sync_status=kwargs.get("sync_status", "PENDING"),
            created_at=kwargs.get("created_at"),
            updated_at=kwargs.get("updated_at")
        )