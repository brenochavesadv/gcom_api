from main import db

class UsersGroup(db.Model):
    __bind_key__ = 'main'  # SQLAlchemy to use the 'main' bind
    __tablename__ = "users_grp"

    users_grp_id = db.Column(db.Integer, primary_key=True)
    nome_grupo = db.Column(db.String, primary_key=False)
    instit_id_fk = db.Column(db.Integer, primary_key=False)
    acess = db.Column(db.String, primary_key=False)
    data_criacao = db.Column(db.TIMESTAMP(timezone=True), primary_key=False)
    data_atualizacao = db.Column(db.TIMESTAMP(timezone=True), primary_key=False)
