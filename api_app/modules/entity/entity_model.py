from main import db

class Entity(db.Model):
    __bind_key__ = 'main'  # SQLAlchemy to use the 'main' bind
    __tablename__ = "instit"

    id = db.Column("instit_id",db.Integer, primary_key=True)
    entity_main_id = db.Column("instit_matriz_id",db.Integer, primary_key=False)
    person_control_id_fk = db.Column("pescod_id_fk", db.Integer, primary_key=False)
    active = db.Column("ativo", db.Integer, primary_key=False)
    name = db.Column("nome", db.String(255), primary_key=False)
    phone = db.Column("telefone", db.String(20), primary_key=False)
    slogan = db.Column("slogan", db.String(255), primary_key=False)
    active_modules = db.Column("modulos", db.String(255), primary_key=False)

    def to_dict(self):
        result = {
            'id': self.id,
            'entity_main_id': self.entity_main_id,
            'person_control_id_fk': self.person_control_id_fk,
            'active': bool(self.active) if self.active == 1 else False,
            'name': self.name,
            'phone': self.phone,
            'slogan': self.slogan,
            'active_modules': self.active_modules,
        }
        return result

