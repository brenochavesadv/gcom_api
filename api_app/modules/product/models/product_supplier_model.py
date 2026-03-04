from main import db

class ProductSupplier(db.Model):
    __bind_key__ = 'sales'  # SQLAlchemy to use the 'product' bind
    __tablename__ = "prod_forn"

    uid = db.Column("fabpro_id", db.Integer, primary_key=True)
    organization_uid_fk = db.Column("instit_id_fk", db.Integer, primary_key=False)
    product_id_fk = db.Column("produtos_id_fk", db.Integer, primary_key=False)  
    person_uid_fk = db.Column("fabr", db.String, primary_key=False)
    brand = db.Column("marca", db.String, primary_key=False)
    product_supplier_code = db.Column("prod_cod_forn", db.String, primary_key=False)



    def to_dict(self):
        """Convert model to dictionary using direct attribute access"""
        return {
            'uid': self.uid,
            'organization_uid_fk': self.organization_uid_fk,
            'product_id_fk': self.product_id_fk,
            'person_uid_fk': self.person_uid_fk,
            'brand': self.brand,
            'product_supplier_code': self.product_supplier_code,
        }


def __repr__(self):
    return f"<ProductSupplier {self.uid}>"

def __str__(self):
    return self.__repr__()

@staticmethod
def create(**kwargs):
    return ProductSupplier(
        organization_uid_fk=kwargs.get("organization_uid_fk"),
        product_id_fk=kwargs.get("product_id_fk"),
        person_uid_fk=kwargs.get("person_uid_fk"),
        brand=kwargs.get("brand"),
        product_supplier_code=kwargs.get("product_supplier_code"),
    )