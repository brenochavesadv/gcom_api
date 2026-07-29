from main import db

class ProductCount(db.Model):
    __bind_key__ = 'DB_MAIN' 
    __tablename__ = "product_count"

    uid = db.Column(db.Integer, primary_key=True)
    product_uid_fk = db.Column(db.Integer, db.ForeignKey("produtos.produtos_id"), nullable=False)
    current_tax_inventory = db.Column(db.Numeric, nullable=False)
    current_front_inventory = db.Column(db.Numeric, nullable=False)
    current_warehouse_inventory = db.Column(db.Numeric, nullable=False)
    audited_tax_inventory = db.Column(db.Numeric, nullable=False)
    audited_front_inventory = db.Column(db.Numeric, nullable=False)
    audited_warehouse_inventory = db.Column(db.Numeric, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

    products = db.relationship("Product", back_populates="product_count", lazy=True)
