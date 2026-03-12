from main import db
from datetime import datetime
from pytz import UTC

class Users(db.Model):
    #__bind_key__ = 'main'  # SQLAlchemy to use the 'main' bind
    __tablename__ = "users"

    user_uid = db.Column('users_id', db.Integer, primary_key=True)
    person_uid_fk = db.Column('pescod_id_fk', db.Integer)
    organization_uid_fk = db.Column('instit_id_fk', db.Integer)
    is_active = db.Column('ativo', db.Integer)
    user_group_id_fk = db.Column('users_grp_id_fk', db.Integer)
    login = db.Column('login', db.String(25))
    name = db.Column('nome', db.String(100))
    numlog = db.Column('numlog', db.Integer)
    pin_code = db.Column('senha', db.String(10))
    permissions = db.Column('acess', db.String(255))
    is_developer = db.Column('desenv', db.Integer)
    pin_date = db.Column('data_senha', db.TIMESTAMP(timezone=True))
    created_at = db.Column('data_criacao', db.TIMESTAMP(timezone=True))
    updated_at = db.Column('data_atualizacao', db.TIMESTAMP(timezone=True))

    def to_dict(self, datetime_format='iso'):
        """Convert model to dictionary using direct attribute access"""
        result = {
            'user_uid': self.user_uid,
            'person_uid_fk': self.person_uid_fk,
            'organization_uid_fk': self.organization_uid_fk,
            'is_active': bool(self.is_active) if self.is_active == 1 else False,
            'user_group_id_fk': self.user_group_id_fk,
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
        return f"<User {self.user_uid} - {self.name}>"

    def __str__(self):
        return f"User(user_uid={self.user_uid}, name={self.name}, login={self.login})"