from backend.apps.commerciall_api.main import db


class IcmsPisCofinsItem (db.Model):
    __tablename__ = 'product_tax_br_icms_pis_cofins_item'

    uid = db.Column(db.String(36), primary_key=True)
    icms_pis_cofins_group_uid_fk = db.Column(db.String(36), db.ForeignKey('product_tax_br_icms_pis_cofins_group.uid'), nullable=False)
    cfop = db.Column(db.Integer, nullable=False, default=0)
    csosn = db.Column(db.Integer, nullable=False, default=0)
    cst_icms = db.Column(db.Integer, nullable=False, default=0)
    aliquota_nominal_icms = db.Column(db.Float, nullable=False, default=0.0)
    reducao_base_nominal_icms = db.Column(db.Float, nullable=False, default=0.0)
    aliquota_efetiva_icms = db.Column(db.Float, nullable=False, default=0.0)
    reducao_base_efetiva_icms = db.Column(db.Float, nullable=False, default=0.0)
    aliquota_fundo_combate_pobreza = db.Column(db.Float, nullable=False, default=0.0)
    cst_pis = db.Column(db.Integer, nullable=False, default=0)
    aliquota_pis = db.Column(db.Float, nullable=False, default=0.0)
    cod_receita_pis = db.Column(db.Integer, nullable=False, default=0)
    cod_credito_pis = db.Column(db.Integer, nullable=False, default=0)
    cst_cofins = db.Column(db.Integer, nullable=False, default=0)
    aliquota_cofins = db.Column(db.Float, nullable=False, default=0.0)
    cod_receita_cofins = db.Column(db.Integer, nullable=False, default=0)
    cod_credito_cofins = db.Column(db.Integer, nullable=False, default=0)
    cod_base_calculo_credito_pis_cofins = db.Column(db.Integer, nullable=False, default=0)
    cod_contribuicao_social_apurada = db.Column(db.Integer, nullable=False, default=0)
    account_section_uid_fk = db.Column(db.Integer, nullable=False, default=0)
    sync_status = db.Column(db.String(10), nullable=False, default="PENDING")
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)

    @staticmethod
    def from_json(data):
        return IcmsPisCofinsItem(
            uid=data.get("uid"),
            icms_pis_cofins_group_uid_fk=data.get("icms_pis_cofins_group_uid_fk"),
            cfop=data.get("cfop"),
            csosn=data.get("csosn"),
            cst_icms=data.get("cst_icms"),
            aliquota_nominal_icms=data.get("aliquota_nominal_icms"),
            reducao_base_nominal_icms=data.get("reducao_base_nominal_icms"),
            aliquota_efetiva_icms=data.get("aliquota_efetiva_icms"),
            reducao_base_efetiva_icms=data.get("reducao_base_efetiva_icms"),
            aliquota_fundo_combate_pobreza=data.get("aliquota_fundo_combate_pobreza"),
            cst_pis=data.get("cst_pis"),
            aliquota_pis=data.get("aliquota_pis"),
            cod_receita_pis=data.get("cod_receita_pis"),
            cod_credito_pis=data.get("cod_credito_pis"),
            cst_cofins=data.get("cst_cofins"),
            aliquota_cofins=data.get("aliquota_cofins"),
            cod_receita_cofins=data.get("cod_receita_cofins"),
            cod_credito_cofins=data.get("cod_credito_cofins"),
            cod_base_calculo_credito_pis_cofins=data.get("cod_base_calculo_credito_pis_cofins"),
            cod_contribuicao_social_apurada=data.get("cod_contribuicao_social_apurada"),
            account_section_uid_fk=data.get("account_section_uid_fk"),
            sync_status=data.get("sync_status"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )

    def to_dict(self):
        return {
            "uid": self.uid,
            "icms_pis_cofins_group_uid_fk": self.icms_pis_cofins_group_uid_fk,
            "cfop": self.cfop,
            "csosn": self.csosn,
            "cst_icms": self.cst_icms,
            "aliquota_nominal_icms": self.aliquota_nominal_icms,
            "reducao_base_nominal_icms": self.reducao_base_nominal_icms,
            "aliquota_efetiva_icms": self.aliquota_efetiva_icms,
            "reducao_base_efetiva_icms": self.reducao_base_efetiva_icms,
            "aliquota_fundo_combate_pobreza": self.aliquota_fundo_combate_pobreza,
            "cst_pis": self.cst_pis,
            "aliquota_pis": self.aliquota_pis,
            "cod_receita_pis": self.cod_receita_pis,
            "cod_credito_pis": self.cod_credito_pis,
            "cst_cofins": self.cst_cofins,
            "aliquota_cofins": self.aliquota_cofins,
            "cod_receita_cofins": self.cod_receita_cofins,
            "cod_credito_cofins": self.cod_credito_cofins,
            "cod_base_calculo_credito_pis_cofins": self.cod_base_calculo_credito_pis_cofins,
            "cod_contribuicao_social_apurada": self.cod_contribuicao_social_apurada,
            "account_section_uid_fk": self.account_section_uid_fk,
            "sync_status": self.sync_status,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    def updatable_fields(self, other):
            _updatable_fields = [
                'cfop',
                'csosn',
                'cst_icms',
                'aliquota_nominal_icms',
                'reducao_base_nominal_icms',
                'aliquota_efetiva_icms',
                'reducao_base_efetiva_icms',
                'aliquota_fundo_combate_pobreza',
                'cst_pis',
                'aliquota_pis',
                'cod_receita_pis',
                'cod_credito_pis',
                'cst_cofins',
                'aliquota_cofins',
                'cod_receita_cofins',
                'cod_credito_cofins',
                'cod_base_calculo_credito_pis_cofins',
                'cod_contribuicao_social_apurada',
                'account_section_uid_fk', 
            ]
    
            for field in _updatable_fields:
                if hasattr(other, field):
                    setattr(self, field, getattr(other, field))
