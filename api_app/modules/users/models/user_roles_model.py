from main import db
from sqlalchemy.orm import relationship
from .organization_model import Organization
from sqlalchemy.dialects.mysql import LONGTEXT

class UserRoles(db.Model):
    __bind_key__ = 'DB_MAIN' 
    __tablename__ = "user_roles"

    uid = db.Column(db.String(36), unique=True, primary_key=True)
    main_organization_uid_fk = db.Column(db.String(36), db.ForeignKey(Organization.uid))
    name = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(100))
    allowed_app_routes = db.Column(LONGTEXT, nullable=True, default=list)
    sync_status = db.Column(db.String(10))
    created_at = db.Column(db.TIMESTAMP(timezone=True))
    updated_at = db.Column(db.TIMESTAMP(timezone=True))

    organization = relationship("Organization", back_populates="user_roles", foreign_keys=[main_organization_uid_fk])
    user_organizations = relationship("UserOrganizations", back_populates="user_roles", foreign_keys="UserOrganizations.user_roles_uid_fk")

    def to_dict(self):
        return {
            'uid': self.uid,
            'main_organization_uid_fk': self.main_organization_uid_fk,
            'name': self.name,
            'description': self.description,
            'allowed_app_routes': self.allowed_app_routes,
            'sync_status': self.sync_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


    @staticmethod
    def get_data(data):
        if not isinstance(data, dict):
            data = {}

        return {
            'uid': data.get('uid'),
            'main_organization_uid_fk': data.get('main_organization_uid_fk'),
            'name': data.get('name'),
            'description': data.get('description'),
            'allowed_app_routes': data.get('allowed_app_routes'),
            'sync_status': data.get('sync_status', 'PENDING')
        }