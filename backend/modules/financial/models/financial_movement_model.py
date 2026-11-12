from backend.apps.commerciall_api.main import db


class FinancialMovement(db.Model):
    """Mapping for legacy ``contasmv`` ledger entries."""

    __bind_key__ = "DB_MAIN"
    __tablename__ = "contasmv"

    uid = db.Column("id", db.Integer, primary_key=True)
    organization_uid_fk = db.Column("instit", db.Integer, nullable=False)
    account_uid = db.Column("idctfin", db.Integer, nullable=False)
    section_uid = db.Column("idsecao", db.Integer, nullable=False)
    direction = db.Column("tipo", db.Integer, nullable=False)
    description = db.Column("descr", db.String(100), nullable=False)
    amount = db.Column("valor", db.Numeric(12, 2), nullable=False)
    date = db.Column("dat", db.Date, nullable=False)
    origin = db.Column("origem", db.Integer, nullable=False)
    linked_uid = db.Column("idorigem", db.Integer, nullable=True)
    user_uid = db.Column("user", db.Integer, nullable=True)
    is_active = db.Column("sit", db.Integer, nullable=False, default=1)

    def to_dict(self, balance, version=""):
        origins = {0: "opening", 1: "transfer", 2: "manual", 3: "payable", 4: "receipt"}
        directions = {0: "opening", 1: "credit", 2: "debit"}
        return {
            "uid": str(self.uid), "account_uid": str(self.account_uid),
            "date": self.date.isoformat(), "description": self.description,
            "amount": f"{float(self.amount):.2f}", "balance": f"{float(balance):.2f}",
            "origin": origins.get(self.origin, "manual"),
            "direction": directions.get(self.direction, "opening"),
            "linked_uid": str(self.linked_uid or ""), "version": version or str(self.uid),
        }
