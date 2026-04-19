from main import db
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import LONGTEXT


class OrganizationRoutes(db.Model):
    __bind_key__ = 'DB_MAIN' 
    __tablename__ = "organization_routes"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    main_organization_uid_fk = db.Column(db.String(36), db.ForeignKey('organization.uid'))
    app_routes_uid = db.Column(LONGTEXT, nullable=False)  # Comma-separated list of child route identifiers

    organization = relationship("Organization", back_populates="organization_routes", foreign_keys=[main_organization_uid_fk])
    
    def to_dict(self):
        return {
            'id': self.id,
            'main_organization_uid_fk': self.main_organization_uid_fk,
            'app_routes_uid': self.app_routes_uid,
        }