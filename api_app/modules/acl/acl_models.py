
from main import db

class AclRoles(db.Model):
    __tablename__ = "acl_roles"
    uid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    permissions = db.relationship('AclPermissions', secondary='acl_role_permissions', backref='roles')

class AclPermissions(db.Model):
    __tablename__ = "acl_permissions"
    uid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

class AclRolePermissions(db.Model):
    __tablename__ = "acl_role_permissions"
    uid = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('acl_roles.uid'), primary_key=True)
    permission_id = db.Column(db.Integer, db.ForeignKey('acl_permissions.uid'), primary_key=True)
