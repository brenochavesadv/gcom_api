from sqlalchemy import func
from sqlalchemy.orm import relationship
from api_app.modules.person.models.person_model import Person
from main import db
from sqlalchemy.dialects.mysql import LONGTEXT
import json
from .user_profiles_model import UserProfiles
from .organization_model import Organization
from .user_roles_model import UserRoles

class UserOrganizations(db.Model):
    __bind_key__ = 'DB_MAIN' 
    __tablename__ = "user_organizations"
    
    uid = db.Column(db.String(36), primary_key=True, unique=True)
    user_profiles_uid_fk = db.Column(db.String(36), db.ForeignKey(UserProfiles.uid))
    organization_uid_fk = db.Column(db.String(36), db.ForeignKey(Organization.uid))
    is_active = db.Column(db.Integer, default=0)  # 1 for active, 0 for inactive
    user_roles_uid_fk = db.Column(db.String(36), db.ForeignKey(UserRoles.uid))
    person_uid_fk = db.Column(db.String(36), db.ForeignKey(Person.uid))
    user_name = db.Column(db.String(20), nullable=False)
    sync_status = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())
    allowed_app_routes = db.Column(LONGTEXT, nullable=True, default='[]') # uuid list of allowed app routes stored in the app 

    organization = relationship("Organization", back_populates="user_organizations", foreign_keys=[organization_uid_fk])
    user_profiles = relationship("UserProfiles", back_populates="user_organizations", foreign_keys=[user_profiles_uid_fk])
    user_roles = relationship("UserRoles", back_populates="user_organizations", foreign_keys=[user_roles_uid_fk])
    person = relationship("Person", back_populates="user_organizations", foreign_keys=[person_uid_fk])


    def to_dict(self):
        return {
            'uid': self.uid,
            'user_profiles_uid_fk': self.user_profiles_uid_fk,
            'organization_uid_fk': self.organization_uid_fk,
            'user_roles_uid_fk': self.user_roles_uid_fk,
            'is_active': bool(self.is_active) if self.is_active == 1 else False,
            'person_uid_fk': self.person_uid_fk,
            'user_name': self.user_name,
            'sync_status': self.sync_status,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'allowed_app_routes': self.allowed_app_routes,
            'organization': self.organization.to_dict(),
        }

    def from_json(json_data):
        allowed_app_routes = str(json_data.get('allowed_app_routes', ''))
        allowed_app_routes = allowed_app_routes.replace('[', '').replace(']', '').replace('"', '').replace("'", "")
        return UserOrganizations(
            uid=json_data.get('uid'),
            user_profiles_uid_fk=json_data.get('user_profiles_uid_fk'),
            user_roles_uid_fk=json_data.get('user_roles_uid_fk'),
            organization_uid_fk=json_data.get('organization_uid_fk'),
            person_uid_fk=json_data.get('person_uid_fk'),
            user_name=json_data.get('user_name'),
            sync_status=json_data.get('sync_status'),
            is_active=1 if json_data.get('is_active') else 0,
            allowed_app_routes = allowed_app_routes,
            created_at=json_data.get('created_at'),
            updated_at=json_data.get('updated_at'),
        )