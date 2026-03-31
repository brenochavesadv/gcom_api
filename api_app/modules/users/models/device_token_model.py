from main import db
from datetime import datetime

class DeviceToken(db.Model):
    __tablename__ = 'device_tokens'
    id = db.Column(db.Integer, primary_key=True)
    user_uid = db.Column(db.String(128), nullable=False, index=True)
    token = db.Column(db.String(512), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_uid': self.user_uid,
            'token': self.token,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
