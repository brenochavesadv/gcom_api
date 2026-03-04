from main import db

class UsersGroup(db.Model):
   # __bind_key__ = 'main'  # SQLAlchemy to use the 'main' bind
    __tablename__ = "users_grp"

    user_grp_uid = db.Column(db.Integer, primary_key=True)
    nome_grupo = db.Column(db.String(20))
    instit_id_fk = db.Column(db.Integer)
    acess = db.Column(db.String(100))
    data_criacao = db.Column(db.TIMESTAMP(timezone=True))
    data_atualizacao = db.Column(db.TIMESTAMP(timezone=True))
