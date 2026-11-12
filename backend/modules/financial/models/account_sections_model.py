from backend.apps.commerciall_api.main import db

class AccountSection(db.Model):
    __bind_key__ = 'DB_MAIN'
    __tablename__ = "secoes"

    uid = db.Column('secoes_id', db.Integer, primary_key=True)
    main_organization_uid_fk = db.Column('instit_id_fk', db.Integer, nullable=False, default=0)
    account_code = db.Column('codconta', db.String(20), nullable=False, default='')
    is_active = db.Column('ativo', db.Integer, nullable=False, default=2)
    is_section = db.Column(db.Integer, nullable=False, default=0)
    description = db.Column('secao', db.String(60), nullable=False, default='')
    type = db.Column('tipocod', db.Integer, nullable=False, default=1, comment='0=todos 1=sintetico 2=analitico')
    category = db.Column('tipoconta', db.Integer, nullable=False, default=1, comment='0=todos 1=nenhum 2=receitas 3=contaspg 4=favorecidos 5=cartao')
    reduced_code = db.Column('reduzido', db.Integer, default=0)
    sync_status = db.Column('sync_status', db.String(10), nullable=False, default='PENDING')
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)

    def to_dict(self):
            return {
                "uid": self.uid,
                "main_organization_uid_fk": self.main_organization_uid_fk,
                "account_code": self.account_code,
                "is_active": self.is_active,
                "is_section": self.is_section,
                "description": self.description,
                "type": self.type,
                "category": self.category,
                "reduced_code": self.reduced_code,
                "sync_status": self.sync_status,
                "created_at": self.created_at.isoformat() if self.created_at else None,
                "updated_at": self.updated_at.isoformat() if self.updated_at else None
            }

    @staticmethod
    def from_json(data):
        return AccountSection(
            uid=data.get('uid'),
            main_organization_uid_fk=data.get('main_organization_uid_fk'),
            account_code=data.get('account_code'),
            is_active=data.get('is_active'),
            is_section=data.get('is_section'),
            description=data.get('description'),
            type=data.get('type'),
            category=data.get('category'),
            reduced_code=data.get('reduced_code'),
            sync_status=data.get('sync_status'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )