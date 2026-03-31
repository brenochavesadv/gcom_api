from sqlalchemy import func
from sqlalchemy.orm import relationship
from main import db
import bcrypt
from .user_profiles_model import UserProfiles

class UserKeys(db.Model):
    #__bind_key__ = 'main'  # SQLAlchemy to use the 'main' bind
    __tablename__ = "user_keys"

    user_profiles_uid_fk = db.Column(db.String(36), db.ForeignKey(UserProfiles.uid),  primary_key=True)
    sync_status = db.Column(db.String(10), default="PENDING")
    pin_code = db.Column(db.String(255), nullable=False) 
    pw_offline = db.Column(db.String(255))
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    user_profiles = relationship("UserProfiles", back_populates="user_keys", foreign_keys=[user_profiles_uid_fk])


    def to_dict(self):
        return {            
            'user_profiles_uid_fk': self.user_profiles_uid_fk,
            'sync_status': self.sync_status,
            'pin_code': self.pin_code,      
            'pw_offline': self.pw_offline,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


    def from_json(json_data):
        return UserKeys(
            user_profiles_uid_fk=json_data.get("user_profiles_uid_fk"),
            sync_status=json_data.get("sync_status"),
            pin_code=json_data.get("pin_code"),
            pw_offline=json_data.get("pw_offline"),
            updated_at=json_data.get("updated_at"),
        )

    def bcrypt_hash(pin_code,user_uid):
        return bcrypt.hashpw(
        (f"{pin_code}{user_uid}").encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")