from main import db
from sqlalchemy.orm import relationship

class Organization(db.Model):
    #__bind_key__ = 'main'  # SQLAlchemy to use the 'main' bind
    __tablename__ = "instit"

    id = db.Column("instit_id", db.Integer, primary_key=True)
    uid = db.Column(db.String(36), unique=True, nullable=False)
    main_organization_id = db.Column("instit_matriz_id", db.Integer)
    main_organization_uid = db.Column(db.String(36))
    is_active = db.Column("ativo", db.Integer)    
    name = db.Column("nome", db.String(100))
    phone = db.Column("telefone", db.String(20))
    mail = db.Column(db.String(60))
    site = db.Column(db.String(60))
    address = db.Column(db.String(80))
    address_number = db.Column(db.String(10))
    address_complement = db.Column(db.String(30))
    neighborhood = db.Column(db.String(50))
    city = db.Column(db.String(50))
    state = db.Column(db.String(2))
    zip_code = db.Column(db.String(12))
    country = db.Column(db.String(3))
    instagram = db.Column(db.String(50))
    facebook = db.Column(db.String(50))
    picture = db.Column(db.String(30)) 
    slogan = db.Column(db.String(60))
    active_modules = db.Column("modulos", db.String(100))
    sync_status = db.Column(db.String(10))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    user_roles = relationship("UserRoles", back_populates="organization", lazy='select', foreign_keys="UserRoles.main_organization_uid_fk")
    person = relationship("Person", back_populates="organization", lazy='select', foreign_keys="Person.main_organization_uid_fk")
    user_organizations = relationship("UserOrganizations", back_populates="organization", lazy='select', foreign_keys="UserOrganizations.organization_uid_fk")

    def to_dict(self):

        result = {
            'id': self.id,
            'uid': self.uid,
            'main_organization_id': self.main_organization_id,
            'main_organization_uid': self.main_organization_uid,
            'is_active': bool(self.is_active) if self.is_active == 1 else False,
            'name': self.name,
            'phone': self.phone,
            'mail': self.mail,
            'site': self.site,
            'address': self.address,
            'address_number': self.address_number,
            'address_complement': self.address_complement,
            'neighborhood': self.neighborhood,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'country': self.country,
            'instagram': self.instagram,
            'facebook': self.facebook,
            'picture': self.picture,
            'slogan': self.slogan,
            'active_modules': self.active_modules,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }
        return result


# Imported here (after class definition) to register relationship targets with
# SQLAlchemy's mapper registry before the first query resolves relationships.
from .user_organizations_model import UserOrganizations  # noqa: E402
from .user_roles_model import UserRoles  # noqa: E402