from sqlalchemy import func
from sqlalchemy.orm import relationship
from main import db

class UserOrganizations(db.Model):
    #__bind_key__ = 'main'  # SQLAlchemy to use the 'main' bind
    __tablename__ = "user_organizations"
    
    uid = db.Column(db.String(36), primary_key=True, unique=True)
    user_uid_fk = db.Column(db.String(36), db.ForeignKey('users.uid'))
    organization_uid_fk = db.Column(db.String(36), db.ForeignKey('instit.uid'))
    sync_status = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())
    organization = relationship("Organization", back_populates="user_organizations", foreign_keys=[organization_uid_fk])
    users = relationship("Users", back_populates="user_organizations", foreign_keys=[user_uid_fk])

    def to_dict(self):
        return {
            'uid': self.uid,
            'user_uid_fk': self.user_uid_fk,
            'organization_uid_fk': self.organization_uid_fk,
            'sync_status': self.sync_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def user_organizations_dict(self):
        return {
            'organization_uid': self.organization_uid_fk,
            'organization_name': self.organization.name if self.organization else None
        }