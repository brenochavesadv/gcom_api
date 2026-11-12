from datetime import date, datetime

from backend.apps.commerciall_api.main import db


class FinancialAccount(db.Model):
    """Mapping for the legacy ``contasfin`` financial-account table."""

    __bind_key__ = "DB_MAIN"
    __tablename__ = "contasfin"

    uid = db.Column("contasfin_id", db.Integer, primary_key=True)
    main_organization_uid_fk = db.Column("instit_id_fk", db.Integer, nullable=False)
    is_active = db.Column("sit", db.Integer, nullable=False, default=1)
    type = db.Column("tipo", db.Integer, nullable=False, default=1)
    section_uid = db.Column("secoes_id_fk", db.Integer, nullable=False)
    name = db.Column("nome", db.String(30), nullable=False)
    opening_date = db.Column("dtabr", db.Date, nullable=True)
    opening_balance = db.Column("saldoini", db.Numeric(12, 2), nullable=False, default=0)
    collection_enabled = db.Column("cobr", db.Integer, nullable=False, default=1)
    bank_uid = db.Column("bancos_id_fk", db.Integer, nullable=True)
    agreement = db.Column("conv", db.String(20), nullable=False, default="")
    agreement_digit = db.Column("convdig", db.String(5), nullable=False, default="")
    beneficiary = db.Column("cedente", db.String(80), nullable=False, default="")
    street = db.Column("ced_endlogr", db.String(80), nullable=False, default="")
    number = db.Column("ced_endnum", db.String(10), nullable=False, default="")
    complement = db.Column("ced_endcomp", db.String(40), nullable=False, default="")
    district = db.Column("ced_endbairro", db.String(40), nullable=False, default="")
    postal_code = db.Column("ced_endcep", db.String(12), nullable=False, default="")
    city = db.Column("ced_endcidade", db.String(60), nullable=False, default="")
    state = db.Column("ced_enduf", db.String(2), nullable=False, default="")
    tax_id = db.Column("cpfcnpj", db.String(20), nullable=False, default="")
    beneficiary_code = db.Column("cedcod", db.String(20), nullable=False, default="")
    agency = db.Column("cedagenc", db.String(10), nullable=False, default="")
    agency_digit = db.Column("cedagd", db.String(3), nullable=False, default="")
    account_number = db.Column("cedconta", db.String(20), nullable=False, default="")
    account_digit = db.Column("cedctdig", db.String(3), nullable=False, default="")
    operation = db.Column("oper", db.String(10), nullable=False, default="")
    wallet = db.Column("carteira", db.String(10), nullable=False, default="")
    variation = db.Column("variacao", db.String(10), nullable=False, default="")
    document_species_uid = db.Column("boleto_cb_especie_id_fk", db.Integer, nullable=True)
    instruction_1 = db.Column("instr1", db.String(100), nullable=False, default="")
    instruction_2 = db.Column("instr2", db.String(100), nullable=False, default="")
    instruction_3 = db.Column("instr3", db.String(100), nullable=False, default="")
    currency_uid = db.Column("moedas_id_fk", db.Integer, nullable=True)
    fee = db.Column("taxa", db.Numeric(5, 2), nullable=False, default=0)
    manager = db.Column("gerente", db.String(60), nullable=False, default="")
    phone = db.Column("tel", db.String(30), nullable=False, default="")
    email = db.Column("email", db.String(120), nullable=False, default="")
    monthly_interest_percent = db.Column("mora_mes", db.Numeric(5, 2), nullable=False, default=0)
    protest_days = db.Column("dias_protesto", db.String(3), nullable=False, default="")
    late_fee_percent = db.Column("multa_atraso", db.Numeric(5, 2), nullable=False, default=0)

    def to_dict(self):
        return {
            "uid": str(self.uid),
            "name": self.name,
            "section_uid": str(self.section_uid),
            "type": self.type,
            "is_active": self.is_active == 1,
            "collection_enabled": self.collection_enabled == 2,
            "opening_date": self.opening_date.isoformat() if self.opening_date else None,
            "opening_balance": _decimal(self.opening_balance),
            "bank": {
                "bank_uid": _string(self.bank_uid), "agency": self.agency or "",
                "agency_digit": self.agency_digit or "", "account_number": self.account_number or "",
                "account_digit": self.account_digit or "", "operation": self.operation or "",
                "manager": self.manager or "", "phone": self.phone or "", "email": self.email or "",
                "agreement": self.agreement or "", "agreement_digit": self.agreement_digit or "",
                "wallet": self.wallet or "", "variation": self.variation or "",
                "beneficiary": self.beneficiary or "", "beneficiary_code": self.beneficiary_code or "",
                "tax_id": self.tax_id or "", "street": self.street or "", "number": self.number or "",
                "complement": self.complement or "", "district": self.district or "",
                "postal_code": self.postal_code or "", "city": self.city or "", "state": self.state or "",
                "currency_uid": _string(self.currency_uid),
                "document_species_uid": _string(self.document_species_uid),
                "instruction_1": self.instruction_1 or "", "instruction_2": self.instruction_2 or "",
                "instruction_3": self.instruction_3 or "", "fee": _decimal(self.fee),
                "monthly_interest_percent": _decimal(self.monthly_interest_percent),
                "late_fee_percent": _decimal(self.late_fee_percent), "protest_days": self.protest_days or "",
            },
        }

    @staticmethod
    def from_json(data, main_organization_uid):
        bank = data.get("bank") or {}
        return FinancialAccount(
            uid=int(data["uid"]) if str(data.get("uid", "")).isdigit() else None,
            main_organization_uid_fk=main_organization_uid,
            is_active=1 if data.get("is_active", True) else 0,
            type=data.get("type", 1), section_uid=data.get("section_uid"),
            name=str(data.get("name", "")).strip(),
            opening_date=date.fromisoformat(data["opening_date"]),
            opening_balance=data.get("opening_balance", "0.00"),
            collection_enabled=2 if data.get("collection_enabled", False) else 1,
            **{key: bank.get(key, "") for key in (
                "agreement", "agreement_digit", "beneficiary", "street", "number", "complement",
                "district", "postal_code", "city", "state", "tax_id", "beneficiary_code", "agency",
                "agency_digit", "account_number", "account_digit", "operation", "wallet", "variation",
                "instruction_1", "instruction_2", "instruction_3", "manager", "phone", "email", "protest_days",
            )},
            bank_uid=bank.get("bank_uid") or None,
            document_species_uid=bank.get("document_species_uid") or None,
            currency_uid=bank.get("currency_uid") or None,
            fee=bank.get("fee", "0.00"), monthly_interest_percent=bank.get("monthly_interest_percent", "0.00"),
            late_fee_percent=bank.get("late_fee_percent", "0.00"),
        )


def _decimal(value):
    return f"{float(value or 0):.2f}"


def _string(value):
    return "" if value is None else str(value)
