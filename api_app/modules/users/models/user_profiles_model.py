from sqlalchemy.orm import relationship
from main import db
from .organization_model import Organization

class UserProfiles(db.Model):
    __bind_key__ = 'DB_MAIN' 
    __tablename__ = "user_profiles"

    uid = db.Column(db.String(36), primary_key=True)
    mail = db.Column(db.String(60), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    display_name = db.Column(db.String(25))
    is_developer = db.Column(db.Boolean, default=False)
    location = db.Column(db.String(4))
    language_code = db.Column(db.String(2))
    iso2_alpha = db.Column(db.String(2))
    date_format = db.Column(db.String(10))
    default_organization_uid_fk = db.Column(db.String(36), db.ForeignKey(Organization.uid))    
    sync_status = db.Column(db.String(10))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)   
    
    user_organizations = relationship("UserOrganizations", back_populates="user_profiles", foreign_keys="UserOrganizations.user_profiles_uid_fk")
    user_keys = relationship("UserKeys", back_populates="user_profiles", foreign_keys="UserKeys.user_profiles_uid_fk")

    def to_dict(self, join_orgs=False):
        return {  
            'uid': self.uid,
            'mail': self.mail,
            'name': self.name,
            'display_name': self.display_name,
            'is_developer': True if self.is_developer == 1 else False,
            'location': self.location,
            'language_code': self.language_code,
            'iso2_alpha': self.iso2_alpha,
            'date_format': self.date_format,
            'default_organization_uid_fk': self.default_organization_uid_fk,
            'sync_status': self.sync_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user_organizations': [org.to_dict() for org in self.user_organizations] if join_orgs else None,
            'user_keys': [keys.to_dict() for keys in self.user_keys] if self.user_keys else None
        }

    def from_json(json_data):
        return UserProfiles(
            uid = json_data.get("uid"),
            mail = json_data.get("mail"),
            name = json_data.get("name"),
            display_name = json_data.get("display_name"),
            is_developer = json_data.get("is_developer"),
            location = json_data.get("location"),
            language_code = json_data.get("language_code"),
            iso2_alpha = json_data.get("iso2_alpha"),
            date_format = json_data.get("date_format"),
            default_organization_uid_fk = json_data.get("default_organization_uid_fk"),
            sync_status = json_data.get("sync_status"),
            created_at = json_data.get("created_at"),
            updated_at = json_data.get("updated_at"),
        )