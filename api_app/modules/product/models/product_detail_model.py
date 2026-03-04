from main import db
from sqlalchemy.orm import relationship

class ProductDetail(db.Model):
    __bind_key__ = 'sales'  # Change to 'main' to match Product model
    __tablename__ = "prod_itens"

    uid = db.Column("prod_itens_id", db.Integer, primary_key=True)
    # Fix: Use correct foreign key reference
    product_uid_fk = db.Column("produtos_id_fk", db.Integer , nullable=False)
    organization_uid_fk = db.Column("instit_id_fk", db.Integer, nullable=False)
    main_organization_uid_fk = db.Column("instit_matriz_id_fk", db.Integer, nullable=False)
    internal_code = db.Column("codprod", db.Integer, nullable=False)
    is_active = db.Column("ativo", db.Integer, nullable=False, default=1)
    stock_reduce = db.Column("bxest", db.Integer, nullable=False, default=0)
    stock_lowest = db.Column("est_minimo", db.Numeric(10, 3), nullable=False, default=0.000)
    stock_tax = db.Column("est_fiscal", db.Numeric(10, 3), nullable=False, default=0.000)
    stock_front = db.Column("est_frente", db.Numeric(10, 3), nullable=False, default=0.000)
    stock_storage_1 = db.Column("est_dep1", db.Numeric(10, 3), nullable=False, default=0.000)
    stock_storage_2 = db.Column("est_dep2", db.Numeric(10, 3), nullable=False, default=0.000)
    stock_storage_3 = db.Column("est_dep3", db.Numeric(10, 3), nullable=False, default=0.000)
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
    is_for_rental = db.Column("locavel", db.Integer, nullable=False, default=0)
    rental_price = db.Column("prloc", db.Numeric(10, 2), nullable=False, default=0.00)
    is_wholesale = db.Column("vdatac", db.Integer, nullable=False, default=0)
    wholesale_quantity = db.Column("qtdatac", db.Numeric(10, 3), nullable=False, default=0.000)
    wholesale_price = db.Column("pratac", db.Numeric(10, 2), nullable=False, default=0.00)
    stock_front_localization = db.Column("loc_frente", db.String(50), nullable=True)
    stock_storage_1_localization = db.Column("loc_dep1", db.String(50), nullable=True)
    stock_storage_2_localization = db.Column("loc_dep2", db.String(50), nullable=True)
    stock_storage_3_localization = db.Column("loc_dep3", db.String(50), nullable=True)
    seller_commission = db.Column("comissao_atv", db.Integer, nullable=False, default=0)
    commission_value = db.Column("comissao_val", db.Numeric(5, 2), nullable=False, default=0.00)
    combo_product_uid = db.Column("produtos_id_combo", db.Integer, nullable=True)
    combo_quantity = db.Column("qtd_combo", db.Numeric(10, 3), nullable=False, default=0.000)

    def to_dict(self):  # FIX: Indent inside the class
        """Convert model to dictionary using direct attribute access"""
        return {
            'uid': self.uid,
            'product_uid_fk': self.product_uid_fk,
            'organization_uid_fk': self.organization_uid_fk,
            'main_organization_uid_fk': self.main_organization_uid_fk,
            'internal_code': self.internal_code,
            'is_active': self.is_active,
            'stock_reduce': self.stock_reduce,
            'stock_lowest': str(self.stock_lowest) if self.stock_lowest is not None else "0.000",
            'stock_tax': str(self.stock_tax) if self.stock_tax is not None else "0.000",
            'stock_front': str(self.stock_front) if self.stock_front is not None else "0.000",
            'stock_storage_1': str(self.stock_storage_1) if self.stock_storage_1 is not None else "0.000",
            'stock_storage_2': str(self.stock_storage_2) if self.stock_storage_2 is not None else "0.000",
            'stock_storage_3': str(self.stock_storage_3) if self.stock_storage_3 is not None else "0.000",
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
            'wholesale_quantity': str(self.wholesale_quantity) if self.wholesale_quantity is not None else "0.000",
            'wholesale_price': str(self.wholesale_price) if self.wholesale_price is not None else "0.000",
            'stock_front_localization': self.stock_front_localization,
            'stock_storage_1_localization': self.stock_storage_1_localization,
            'stock_storage_2_localization': self.stock_storage_2_localization,
            'stock_storage_3_localization': self.stock_storage_3_localization,
            'seller_commission': self.seller_commission,
            'commission_value': str(self.commission_value) if self.commission_value is not None else "0.000",
            'combo_product_id': self.combo_product_id,
            'combo_quantity': str(self.combo_quantity) if self.combo_quantity is not None else "0.000",
        }

    def __repr__(self):  # FIX: Indent inside the class
        return f"<ProductDetail {self.uid}>"

    def __str__(self):  # FIX: Indent inside the class
        return self.__repr__()

    @staticmethod  # FIX: Indent inside the class
    def create(**kwargs):
        return ProductDetail(
            product_uid_fk=kwargs.get("product_uid_fk"),
            organization_uid_fk=kwargs.get("organization_uid_fk"),
            main_organization_uid_fk=kwargs.get("main_organization_uid_fk"),
            internal_code=kwargs.get("internal_code"),
            is_active=kwargs.get("is_active", 1),
            stock_reduce=kwargs.get("stock_reduce", 0),
            stock_lowest=kwargs.get("stock_lowest", 0.000),
            stock_tax=kwargs.get("stock_tax", 0.000),
            stock_front=kwargs.get("stock_front", 0.000),
            stock_storage_1=kwargs.get("stock_storage_1", 0.000),
            stock_storage_2=kwargs.get("stock_storage_2", 0.000),
            stock_storage_3=kwargs.get("stock_storage_3", 0.000),
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
            wholesale_quantity=kwargs.get("wholesale_quantity", 0.000),
            wholesale_price=kwargs.get("wholesale_price", 0.00),
            stock_front_localization=kwargs.get("stock_front_localization"),
            stock_storage_1_localization=kwargs.get("stock_storage_1_localization"),
            stock_storage_2_localization=kwargs.get("stock_storage_2_localization"),
            stock_storage_3_localization=kwargs.get("stock_storage_3_localization"),
            seller_commission=kwargs.get("seller_commission", 0),
            commission_value=kwargs.get("commission_value", 0.00),
            combo_product_id=kwargs.get("combo_product_id"),
            combo_quantity=kwargs.get("combo_quantity", 0.000),
        )