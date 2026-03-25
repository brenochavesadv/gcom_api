from sqlalchemy import func
from sqlalchemy.orm import relationship
from sqlalchemy.exc import ProgrammingError
from main import db
from ...person.models.person_model import Person
from .user_organizations_model import UserOrganizations
from .organization_model import Organization
import bcrypt

class Users(db.Model):
    #__bind_key__ = 'main'  # SQLAlchemy to use the 'main' bind
    __tablename__ = "users"

    id = db.Column("users_id", db.Integer, primary_key=True)
    uid = db.Column(db.String(36), unique=True, nullable=False)
    pescod_id_fk = db.Column("pescod_id_fk", db.Integer, db.ForeignKey('pescod.pescod_id'))
    mail = db.Column(db.String(60), unique=True, nullable=False)
    name = db.Column("nome", db.String(100))
    display_name = db.Column(db.String(25))
    instit_id_fk = db.Column("instit_id_fk", db.Integer)
    is_active = db.Column("ativo", db.Boolean, default=False)
    users_grp_id_fk = db.Column("users_grp_id_fk", db.Integer)
    login = db.Column('login',db.String(20), unique=True)
    numlog = db.Column("numlog", db.Integer, default=0)
    senha = db.Column("senha", db.String(10))
    acess = db.Column("acess", db.String(255))
    is_developer = db.Column("desenv", db.Boolean, default=False)
    pin_updated_at = db.Column("data_senha", db.DateTime)
    created_at = db.Column("data_criacao", db.DateTime, server_default=func.now())
    updated_at = db.Column("data_atualizacao", db.DateTime)   
    location = db.Column(db.String(4))
    language_code = db.Column(db.String(2))
    iso2_alpha = db.Column(db.String(2))
    date_format = db.Column(db.String(10))
    default_organization_uid_fk = db.Column(db.String(36), db.ForeignKey('instit.uid'))    
    sync_status = db.Column(db.String(10))
    pin_code = db.Column(db.String(255), nullable=False) 
    pw_offline = db.Column(db.String(255))
    
    organization = relationship("Organization", back_populates="users", foreign_keys=[default_organization_uid_fk])
    user_organizations = relationship("UserOrganizations", back_populates="users", foreign_keys="UserOrganizations.users_uid_fk")

    def to_dict(self, join_orgs=False):
        return {            
            'id': self.id,
            'uid': self.uid,
            'pescod_id_fk': self.pescod_id_fk,
            'mail': self.mail,
            'name': self.name,
            'display_name': self.display_name,
            'instit_id_fk': self.instit_id_fk,
            'is_active': True if self.is_active == 1 else False,
            'users_grp_id_fk': self.users_grp_id_fk,
            'login': self.login,
            'numlog': self.numlog,
            'senha': self.senha,
            'acess': self.acess,
            'is_developer': self.is_developer,
            'pin_updated_at': self.pin_updated_at.isoformat() if self.pin_updated_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'location': self.location,
            'language_code': self.language_code,
            'iso2_alpha': self.iso2_alpha,
            'date_format': self.date_format,
            'default_organization_uid_fk': self.default_organization_uid_fk,
            'sync_status': self.sync_status,
            'pin_code': self.pin_code,
            'pw_offline': self.pw_offline,
            'user_organizations': [org.to_dict() for org in self.user_organizations] if join_orgs else None,
        }


    def from_json(json_data):
        return Users(
            id=json_data.get("id"),
            uid=json_data.get("uid"),
            pescod_id_fk=json_data.get("pescod_id_fk"),
            mail=json_data.get("mail"),
            name=json_data.get("name"),
            display_name=json_data.get("display_name"),
            instit_id_fk=json_data.get("instit_id_fk"),
            is_active=json_data.get("is_active"),
            users_grp_id_fk=json_data.get("users_grp_id_fk"),
            login=json_data.get("login"),
            numlog=json_data.get("numlog"),
            senha=json_data.get("senha"),
            acess=json_data.get("acess"),
            is_developer=json_data.get("is_developer"),
            pin_updated_at=json_data.get("pin_updated_at"),
            created_at=json_data.get("created_at"),
            updated_at=json_data.get("updated_at"),
            location=json_data.get("location"),
            language_code=json_data.get("language_code"),
            iso2_alpha=json_data.get("iso2_alpha"),
            date_format=json_data.get("date_format"),
            pin_code=json_data.get("pin_code"),
            pw_offline=json_data.get("pw_offline"),
            default_organization_uid_fk=json_data.get("default_organization_uid_fk"),
            sync_status=json_data.get("sync_status"),
        )

    def bcrypt_hash(pin_code,user_uid):
        return bcrypt.hashpw(
        (f"{pin_code}{user_uid}").encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")