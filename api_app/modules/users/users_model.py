from sqlalchemy import func
from sqlalchemy.orm import relationship
from main import db
from ..person.models.person_model import Person
from .users_group_model import UsersGroup

class Users(db.Model):
    #__bind_key__ = 'main'  # SQLAlchemy to use the 'main' bind
    __tablename__ = "users"

    id = db.Column("users_id", db.Integer, primary_key=True)
    uid = db.Column(db.String(36), unique=True, nullable=False)
    pescod_id_fk = db.Column("pescod_id_fk", db.Integer, db.ForeignKey('pescod.pescod_id'))
    person_uid_fk = db.Column("person_uid_fk", db.String(36), db.ForeignKey('pescod.uid'))
    mail = db.Column(db.String(60), unique=True, nullable=False)
    name = db.Column("nome", db.String(100))
    display_name = db.Column(db.String(25))
    login = db.Column(db.String(15), unique=True)
    location = db.Column(db.String(4))
    language_code = db.Column(db.String(2))
    iso2_alpha = db.Column(db.String(2))
    state = db.Column(db.String(30))
    city = db.Column(db.String(50))
    date_format = db.Column(db.String(10))
    pin_code = db.Column("senha", db.String(10))
    pin_updated_at = db.Column("data_senha", db.DateTime)
    is_developer = db.Column("desenv", db.Boolean, default=False)
    organization_id_fk = db.Column("instit_id_fk", db.Integer, db.ForeignKey('instit.instit_id'))
    default_organization_uid_fk = db.Column(db.String(36), db.ForeignKey('instit.uid'))
    is_active = db.Column("ativo", db.Boolean, default=False)
    login_counter = db.Column("numlog", db.Integer, default=0)
    users_group_uid_fk = db.Column(db.String(36), db.ForeignKey('users_grp.uid'))
    permissions = db.Column("acess", db.String(255))
    user_organizations = db.Column(db.String(255))  # JSON string with organizationUid as key and organizationName as value
    sync_status = db.Column(db.String(10))
    created_at = db.Column("data_criacao", db.DateTime, server_default=func.now())
    updated_at = db.Column("data_atualizacao", db.DateTime)   
    organization = relationship("Organization", back_populates="users", foreign_keys=[default_organization_uid_fk])
    users_group = relationship("UsersGroup", back_populates="users", foreign_keys=[users_group_uid_fk])
    person = relationship("Person", back_populates="users", foreign_keys=[person_uid_fk])

    def to_dict(self):
        return {
            'id': self.id,
            'uid': self.uid,
            'pescod_id_fk': self.pescod_id_fk,
            'person_uid_fk': self.person_uid_fk,
            'mail': self.mail,
            'name': self.name,
            'display_name': self.display_name,
            'login': self.login,
            'location': self.location,
            'language_code': self.language_code,
            'iso2_alpha': self.iso2_alpha,
            'state': self.state,
            'city': self.city,
            'date_format': self.date_format,
            'pin_code': self.pin_code,
            'pin_updated_at': self.pin_updated_at.isoformat() if self.pin_updated_at else None,
            'is_developer': self.is_developer,
            'organization_id_fk': self.organization_id_fk,
            'default_organization_uid_fk': self.default_organization_uid_fk,
            'is_active': bool(self.is_active) if self.is_active == 1 else False,
            'login_counter': self.login_counter,
            'users_group_uid_fk': self.users_group_uid_fk,
            'permissions': self.permissions,
            'user_organizations': self.user_organizations,
            'sync_status': self.sync_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<Users {self.uid}>"

    def __str__(self):
        return f"Users(uid={self.uid}, mail={self.mail}, name={self.name})"

    def from_json(data):
        return Users(
            uid=data.get("uid"),
            mail=data.get("mail"),
            pescod_id_fk=data.get("pescod_id_fk"),
            person_uid_fk=data.get("person_uid_fk"),
            name=data.get("name"),
            display_name=data.get("display_name"),
            login=data.get("login"),
            location=data.get("location"),
            language_code=data.get("language_code"),
            iso2_alpha=data.get("iso2_alpha"),
            state=data.get("state"),
            city=data.get("city"),
            date_format=data.get("date_format"),
            pin_code=data.get("pin_code"),
            pin_updated_at=data.get("pin_updated_at"),
            is_developer=data.get("is_developer"),
            organization_id_fk=data.get("organization_id_fk"),
            default_organization_uid_fk=data.get("default_organization_uid_fk"),
            is_active=data.get("is_active"),
            login_counter=data.get("login_counter"),
            users_group_uid_fk=data.get("users_group_uid_fk"),
            permissions=data.get("permissions"),
            user_organizations=data.get("user_organizations"),
            sync_status=data.get("sync_status")
        )