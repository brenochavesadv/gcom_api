from sqlalchemy import func
from sqlalchemy.orm import relationship
from main import db
from sqlalchemy.dialects.mysql import LONGTEXT
import json


class UserOrganizations(db.Model):
    #__bind_key__ = 'main'  # SQLAlchemy to use the 'main' bind
    __tablename__ = "user_organizations"
    
    uid = db.Column(db.String(36), primary_key=True, unique=True)
    users_uid_fk = db.Column(db.String(36), db.ForeignKey('users.uid'))
    organization_uid_fk = db.Column(db.String(36), db.ForeignKey('instit.uid'))
    is_active = db.Column(db.Integer, default=0)  # 1 for active, 0 for inactive
    users_roles_uid_fk = db.Column(db.String(36), db.ForeignKey('users_roles.uid'))
    person_uid_fk = db.Column(db.String(36), db.ForeignKey('pescod.uid'))
    user_name = db.Column(db.String(20), nullable=False)
    sync_status = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())
    allowed_app_routes = db.Column(LONGTEXT, nullable=True, default='[]') # uuid list of allowed app routes stored in the app 

    organization = relationship("Organization", back_populates="user_organizations", foreign_keys=[organization_uid_fk])
    users = relationship("Users", back_populates="user_organizations", foreign_keys=[users_uid_fk])
    users_roles = relationship("UsersRoles", back_populates="user_organizations", foreign_keys=[users_roles_uid_fk])
    person = relationship("Person", back_populates="user_organizations", foreign_keys=[person_uid_fk])


    def to_dict(self):
        return {
            'uid': self.uid,
            'users_uid_fk': self.users_uid_fk,
            'organization_uid_fk': self.organization_uid_fk,
            'users_roles_uid_fk': self.users_roles_uid_fk,
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
        allowed_app_routes = json_data.get('allowed_app_routes', [])
        if isinstance(allowed_app_routes, (list, dict)):
            allowed_app_routes = json.dumps(allowed_app_routes)
        elif allowed_app_routes is None:
            allowed_app_routes = '[]'

        users_roles_uid_fk = json_data.get('users_roles_uid_fk') or None
        created_at = json_data.get('created_at')
        updated_at = json_data.get('updated_at')

        return UserOrganizations(
            uid=json_data.get('uid'),
            users_uid_fk=json_data.get('users_uid_fk'),
            users_roles_uid_fk=users_roles_uid_fk,
            organization_uid_fk=json_data.get('organization_uid_fk'),
            person_uid_fk=json_data.get('person_uid_fk'),
            user_name=json_data.get('user_name'),
            sync_status=json_data.get('sync_status'),
            is_active=1 if json_data.get('is_active') else 0,
            created_at=created_at if created_at not in ('', None) else None,
            updated_at=updated_at if updated_at not in ('', None) else None,
            allowed_app_routes=allowed_app_routes
        )