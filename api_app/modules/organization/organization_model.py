from main import db

class Organization(db.Model):
    #__bind_key__ = 'main'  # SQLAlchemy to use the 'main' bind
    __tablename__ = "instit"

    id = db.Column("id", db.Integer, primary_key=True)
    organization_uid = db.Column("instit_id", db.Integer, primary_key=True)
    organization_main_uid = db.Column("instit_matriz_id", db.Integer)
    is_active = db.Column("ativo", db.Integer)    
    name = db.Column("nome", db.String(100))
    phone = db.Column("telefone", db.String(20))
    mail = db.Column("email", db.String(100))
    site = db.Column("site", db.String(100))
    address = db.Column("endereco", db.String(150))
    address_number = db.Column("numero", db.String(20))
    address_complement = db.Column("complemento", db.String(50))
    neighborhood = db.Column("bairro", db.String(70))
    city = db.Column("cidade", db.String(70))
    state = db.Column("estado", db.String(2))
    zip_code = db.Column("cep", db.String(10))
    country = db.Column("pais", db.String(3))
    instagram = db.Column("instagram", db.String(50))
    facebook = db.Column("facebook", db.String(50))
    picture = db.Column("foto", db.String(30)) 
    slogan = db.Column("slogan", db.String(100))
    active_modules = db.Column("modulos", db.String(100))
    created_at = db.Column("data_criacao", db.DateTime)
    updated_at = db.Column("data_atualizacao", db.DateTime)

    def to_dict(self):
        result = {
            'id': self.id,
            'organization_uid': str(self.organization_uid),
            'organization_main_uid': str(self.organization_main_uid),
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