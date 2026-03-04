from datetime import datetime
from main import db

class ProductGroup(db.Model):
    __bind_key__ = 'sales'  # SQLAlchemy to use the 'product' bind
    __tablename__ = "prod_grp"

    uid = db.Column("prod_grp_id", db.Integer, primary_key=True)
    organization_uid_fk = db.Column("instit_id_fk", db.Integer)
    niv = db.Column("niv", db.Integer)
    level_1 = db.Column("nv1", db.String)
    level_1_id = db.Column("nv1id", db.Integer)
    level_2 = db.Column("nv2", db.String)
    level_2_id = db.Column("nv2id", db.Integer)
    level_3 = db.Column("nv3", db.String)
    updated_at = db.Column("data_atz", db.TIMESTAMP(timezone=True))

    def to_dict(self):
        """Convert model to dictionary using direct attribute access"""
        return {
            'uid': self.uid,
            'organization_uid_fk': self.organization_uid_fk,
            'niv': self.niv,
            'level_1': self.level_1 if self.level_1 is not None else "",
            'level_1_id': self.level_1_id if self.level_1_id is not None else 0,
            'level_2': self.level_2 if self.level_2 is not None else "",
            'level_2_id': self.level_2_id if self.level_2_id is not None else 0,
            'level_3': self.level_3 if self.level_3 is not None else "",
            'updated_at': self.updated_at
        }
    
    def __repr__(self):
        return f"<ProdGroup {self.uid} - {self.organization_uid_fk}>"

    def __str__(self):
        return f"ProdGroup(uid={self.uid}, organization_uid_fk={self.organization_uid_fk})"

    # FACTORY FOR PROD_GROUP
    def create(**kwargs):
        return ProductGroup(
            organization_uid_fk=kwargs.get("organization_uid_fk"),
            niv=kwargs.get("niv"),
            level_1=kwargs.get("level_1"),
            level_1_id=kwargs.get("level_1_id"),
            level_2=kwargs.get("level_2"),
            level_2_id=kwargs.get("level_2_id"),
            level_3=kwargs.get("level_3"),
            updated_at=datetime.now()
        )