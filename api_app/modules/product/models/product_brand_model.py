from main import db

class ProductBrand(db.Model):
    __bind_key__ = 'sales'  # SQLAlchemy to use the 'product' bind
    __tablename__ = "fabpro"

    uid = db.Column("fabpro_id", db.Integer, primary_key=True)
    organization_uid_fk = db.Column("instit_id_fk", db.Integer)
    person_uid_fk = db.Column("fabr", db.String)
    brand = db.Column("marca", db.String)
   
    def to_dict(self):
        return {
            "uid": self.uid,
            "organization_uid_fk": self.organization_uid_fk,
            "person_uid_fk": self.person_uid_fk,
            "brand": self.brand
        }
    
    def __repr__(self):
        return f"<ProductBrand {self.uid} - {self.organization_uid_fk}>"

    def __str__(self):
        return f"ProductBrand(uid={self.uid}, organization_uid_fk={self.organization_uid_fk})"

    # factory method
    @staticmethod
    def create(**kwargs):
        return ProductBrand(
            organization_uid_fk=kwargs.get("organization_uid_fk"),
            person_uid_fk=kwargs.get("person_uid_fk"),
            brand=kwargs.get("brand")
        )