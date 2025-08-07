from main import db
from datetime import datetime
from pytz import UTC

class Users(db.Model):
    __bind_key__ = 'main'  # SQLAlchemy to use the 'main' bind
    __tablename__ = "users"

    id = db.Column('users_id', db.Integer, primary_key=True)
    uid = db.Column('users_uid', db.String(50), primary_key=False)
    person_control_id_fk = db.Column('pescod_id_fk', db.Integer, primary_key=False)
    entity_id_fk = db.Column('instit_id_fk', db.Integer, primary_key=False)
    is_active = db.Column('ativo', db.Integer, primary_key=False)
    users_group_id_fk = db.Column('users_grp_id_fk', db.Integer, primary_key=False)
    login = db.Column('login', db.String(25), primary_key=False)
    name = db.Column('nome', db.String(100), primary_key=False)
    numlog = db.Column('numlog', db.Integer, primary_key=False)
    pin_code = db.Column('senha', db.String(10), primary_key=False)
    permissions = db.Column('acess', db.String(255), primary_key=False)
    is_developer = db.Column('desenv', db.Integer, primary_key=False)
    pin_date = db.Column('data_senha', db.TIMESTAMP(timezone=True), primary_key=False)
    created_at = db.Column('data_criacao', db.TIMESTAMP(timezone=True), primary_key=False)
    updated_at = db.Column('data_atualizacao', db.TIMESTAMP(timezone=True), primary_key=False)

    def to_dict(self, datetime_format='iso'):
        """Convert model to dictionary using direct attribute access"""
        result = {
            'id': self.id,
            'uid': self.uid,
            'person_control_id_fk': self.person_control_id_fk,
            'entity_id_fk': self.entity_id_fk,
            'is_active': bool(self.is_active) if self.is_active == 1 else False,
            'users_group_id_fk': self.users_group_id_fk,
            'login': self.login,
            'name': self.name,
            'numlog': self.numlog,
            'pin_code': self.pin_code,
            'permissions': self.permissions,
            'is_developer': bool(self.is_developer) if self.is_developer == 1 else False,
            'pin_date': self.pin_date,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }
        return result

    def __repr__(self):
        return f"<Users {self.id} - {self.name}>"

    def __str__(self):
        return f"Users(id={self.id}, name={self.name}, login={self.login})"