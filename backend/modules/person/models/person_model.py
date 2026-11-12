from backend.apps.commerciall_api.main import db
from sqlalchemy.orm import relationship
from flask import current_app

from backend.modules.person.models.address_model import Address
from backend.modules.person.models.mail_model import Mail
from backend.modules.person.models.person_accounts_model import PersonAccounts
from backend.modules.person.models.person_financial_model import PersonFinancial
from backend.modules.person.models.person_legal_activity_model import PersonLegalActivity
from backend.modules.person.models.person_legal_br_tax_regime_model import PersonLegalBrTaxRegime
from backend.modules.person.models.person_legal_model import PersonLegal
from backend.modules.person.models.person_legal_partner_model import PersonLegalPartner
from backend.modules.person.models.person_natural_model import PersonNatural
from backend.modules.person.models.person_patrimony_model import PersonPatrimony
from backend.modules.person.models.person_supplementary_model import PersonSupplementary
from backend.modules.person.models.phone_model import Phone
from ...utils.parse_json import ParseJson

class Person(db.Model):
    __bind_key__ = 'DB_MAIN' 
    __tablename__ = "pescod"

    uid = db.Column('pescod_id', db.Integer, primary_key=True)
    main_organization_uid_fk = db.Column('instit_id_fk', db.Integer, db.ForeignKey('instit.instit_id')) # the uid for the main organization
    person_type = db.Column('tipo', db.Integer)
    is_active = db.Column('sit', db.Integer, comment="2 for active")
    is_supplier = db.Column('forn', db.Integer)
    id_number = db.Column('cpfcnpj', db.String(25)) # cpf , cnpj
    iso2alpha = db.Column(db.String(2))
    name = db.Column('nomeOrRazaoSocial', db.String(100))
    picture = db.Column('foto', db.String(100))
    img_bites = db.Column('img_bites', db.Integer)
    credit_limit = db.Column('limite', db.Numeric(10, 2), default=0.00)
    credit_balance = db.Column('saldo', db.Numeric(10, 2), default=0.00)
    is_credit_available = db.Column(db.SmallInteger, default=0)  # 0 = not available, 1 = available
    block_exceeding_limit = db.Column(db.SmallInteger, default=1)  # 0 = not blocked, 1 = blocked
    sync_status = db.Column('sync_status', db.String(20), default="PENDING")
    created_at = db.Column('data_criacao', db.TIMESTAMP(timezone=True), default=db.func.now())
    updated_at = db.Column('data_atualizacao', db.TIMESTAMP(timezone=True), default=db.func.now())

    # A person may have multiple phone records.  The parent side of this
    # relationship is therefore a list, even when there is only one phone.
    phones = relationship(
        "Phone",
        back_populates="person",
        lazy="select",
        uselist=True,
        foreign_keys="[Phone.person_uid_fk]",
    )
    mails = relationship("Mail", back_populates="person", lazy='select', foreign_keys="[Mail.person_uid_fk]")
    addresses = relationship("Address", back_populates="person", lazy='select', foreign_keys="[Address.person_uid_fk]")
    accounts = relationship("PersonAccounts", back_populates="person", lazy='select', foreign_keys="[PersonAccounts.person_uid_fk]")
    financial = relationship("PersonFinancial", back_populates="person", uselist=False, foreign_keys="[PersonFinancial.person_uid_fk]")
    legal = relationship("PersonLegal", back_populates="person", uselist=False, foreign_keys="[PersonLegal.person_uid_fk]")
    br_tax_regimes = relationship("PersonLegalBrTaxRegime", back_populates="person", lazy='select', foreign_keys="[PersonLegalBrTaxRegime.person_uid_fk]")
    activities = relationship("PersonLegalActivity", back_populates="person", lazy='select', foreign_keys="[PersonLegalActivity.person_uid_fk]")
    partners = relationship("PersonLegalPartner", back_populates="person", lazy='select', foreign_keys="[PersonLegalPartner.person_uid_fk]")
    natural = relationship("PersonNatural", back_populates="person", uselist=False, foreign_keys="[PersonNatural.person_uid_fk]")
    patrimonies = relationship("PersonPatrimony", back_populates="person", lazy='select', foreign_keys="[PersonPatrimony.person_uid_fk]")
    supplementary = relationship("PersonSupplementary", back_populates="person", uselist=False, foreign_keys="[PersonSupplementary.person_uid_fk]")
    user_organizations = relationship("UserOrganizations", back_populates="person", lazy='select', foreign_keys="[UserOrganizations.person_uid_fk]")
    product_suppliers = relationship("ProductSupplier", back_populates="person", lazy='select', foreign_keys="[ProductSupplier.person_uid_fk]")
    organization = relationship("Organization", back_populates="person", foreign_keys=[main_organization_uid_fk])
    vehycle_drivers = relationship("VehycleDrivers", back_populates="person", lazy='select', foreign_keys="[VehycleDrivers.person_uid_fk]")
    
    #pronoun = relationship("Pronoun", back_populates="persons", lazy='select')

    # Convert the model to a dictionary representation using plural when is list

    def to_dict_only_person(self):
            return {
                'uid': self.uid,
                'main_organization_uid_fk': self.main_organization_uid_fk,
                'person_type': self.person_type,
                'is_active': ParseJson.return_int_for_true(self.is_active, 2),
                'is_supplier': ParseJson.return_int_for_true(self.is_supplier, 1),
                'id_number': self.id_number,
                'iso2alpha': self.iso2alpha if self.iso2alpha is not None else "",
                'name': self.name,
                'picture': self.picture if self.picture is not None else "nofoto.gif",
                'img_bites': self.img_bites if self.img_bites is not None else 0,
                'credit_limit': float(self.credit_limit) if self.credit_limit is not None else 0,
                'credit_balance': float(self.credit_balance) if self.credit_balance is not None else 0,
                'is_credit_available': ParseJson.return_int_for_true(self.is_credit_available, 1),
                'block_exceeding_limit': ParseJson.return_int_for_true(self.block_exceeding_limit, 1),
                'sync_status': self.sync_status,
                'created_at': self.created_at,
                'updated_at': self.updated_at,
            }
            
    def to_dict(self):
        return {
            **self.to_dict_only_person(),
            'financial': self.financial.to_dict() if self.financial else None,
            'legal': self.legal.to_dict() if self.legal else None,
            'natural': self.natural.to_dict() if self.natural else None,
            'supplementary': self.supplementary.to_dict() if self.supplementary else None,
            'phones': [phone.to_dict() for phone in self.phones] if self.phones else [],
            'mails': [mail.to_dict() for mail in self.mails] if self.mails else [],
            'addresses': [address.to_dict() for address in self.addresses] if self.addresses else [],
            'accounts': [account.to_dict() for account in self.accounts] if self.accounts else [],
            'br_tax_regimes': [item.to_dict() for item in self.br_tax_regimes] if self.br_tax_regimes else [],
            'activities': [item.to_dict() for item in self.activities] if self.activities else [],
            'partners': [item.to_dict() for item in self.partners] if self.partners else [],
            'patrimonies': [item.to_dict() for item in self.patrimonies] if self.patrimonies else [],
        }

    @staticmethod
    def from_json(data):
        current_app.logger.debug(f"Received person data: {data}")
        return Person(    
            uid=int(data.get("uid")) if data.get("uid") is not None else None,
            main_organization_uid_fk=(0 if data.get("main_organization_uid_fk") in ("", None) else
                int(data.get("main_organization_uid_fk"))
            ),
            person_type=data.get("person_type"),
            is_active=ParseJson.return_int_for_true(data.get("is_active"), 2),  # 2 for active, 1 for inactive
            is_supplier=ParseJson.return_int_for_true(data.get("is_supplier"), 1),  # 1 for supplier, 0 for not supplier
            id_number=data.get("id_number"),
            iso2alpha=data.get("iso2alpha"),
            name=data.get("name"),
            picture=data.get("picture"),
            img_bites=8878,  # default value
            credit_limit=data.get("credit_limit"),
            credit_balance=data.get("credit_balance"),
            is_credit_available=data.get("is_credit_available"),
            block_exceeding_limit=int(data.get("block_exceeding_limit")) if data.get("block_exceeding_limit") is not None else 1,  # default to 1 (blocked) if not provided
            sync_status=data.get("sync_status"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),

        )
"""  # CREATES A FACTORY FOR PERSON_MODEL:
    @staticmethod
    def from_json(data):
        current_app.logger.debug(f"Received person data: {data}")

        person = Person(    
            uid=int(data.get("uid")) if data.get("uid") is not None else None,
            main_organization_uid_fk=(0 if data.get("main_organization_uid_fk") in ("", None) else
                int(data.get("main_organization_uid_fk"))
            ),
            person_type=data.get("person_type"),
            is_active=ParseJson.return_int_for_true(data.get("is_active"), 2),  # 2 for active, 1 for inactive
            is_supplier=ParseJson.return_int_for_true(data.get("is_supplier"), 1),  # 1 for supplier, 0 for not supplier
            id_number=data.get("id_number"),
            iso2alpha=data.get("iso2alpha"),
            name=data.get("name"),
            picture=data.get("picture"),
            img_bites=8878,  # default value
            credit_limit=data.get("credit_limit"),
            credit_balance=data.get("credit_balance"),
            is_credit_available=data.get("is_credit_available"),
            block_exceeding_limit=int(data.get("block_exceeding_limit")) if data.get("block_exceeding_limit") is not None else 1,  # default to 1 (blocked) if not provided
            financial=PersonFinancial.from_json(data["financial"])
                if isinstance(data.get("financial"), dict) else None,
            legal=PersonLegal.from_json(data["legal"])
                if isinstance(data.get("legal"), dict) else None,
            natural=PersonNatural.from_json(data["natural"])
                if isinstance(data.get("natural"), dict) else None,
            supplementary=PersonSupplementary.from_json(data["supplementary"])
                if isinstance(data.get("supplementary"), dict) else None,
            mails = [Mail.from_json(mail_data) for mail_data in data.get("mails", [])],
            phones = [Phone.from_json(phone_data) for phone_data in data.get("phones", [])],
            addresses = [Address.from_json(address_data) for address_data in data.get("addresses", [])],
            accounts = [PersonAccounts.from_json(account_data) for account_data in data.get("accounts", [])],
            br_tax_regimes = [PersonLegalBrTaxRegime.from_json(regime_data) for regime_data in data.get("br_tax_regimes", [])],
            activities = [PersonLegalActivity.from_json(activity_data) for activity_data in data.get("activities", [])],
            partners = [PersonLegalPartner.from_json(partner_data) for partner_data in data.get("partners", [])],
            patrimonies = [PersonPatrimony.from_json(patrimony_data) for patrimony_data in data.get("patrimonies", [])],
        )
        return person """
