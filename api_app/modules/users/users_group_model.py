from main import db
from sqlalchemy.orm import relationship

class UsersGroup(db.Model):
  # __bind_key__ = 'main'  # SQLAlchemy to use the 'main' bind
    __tablename__ = "users_grp"

    id = db.Column("users_grp_id", db.Integer, primary_key=True)
    uid = db.Column(db.String(36), unique=True)
    organization_id_fk = db.Column("instit_id_fk", db.Integer, db.ForeignKey('instit.instit_id'))
    organization_uid_fk = db.Column(db.String(36), db.ForeignKey('instit.uid'))
    name = db.Column("nome_grupo", db.String(20))
    permissions = db.Column("acess", db.String(100))
    created_at = db.Column("data_criacao", db.TIMESTAMP(timezone=True))
    updated_at = db.Column("data_atualizacao", db.TIMESTAMP(timezone=True))

    organization = relationship("Organization", back_populates="users_group", foreign_keys=[organization_uid_fk])
    users = relationship("Users", back_populates="users_group", foreign_keys="Users.users_group_uid_fk")
