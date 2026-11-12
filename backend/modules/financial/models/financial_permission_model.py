from backend.apps.commerciall_api.main import db


class FinancialPermission(db.Model):
    """Per-user financial-account access flags from ``contasfin_usu``."""

    __bind_key__ = "DB_MAIN"
    __tablename__ = "contasfin_usu"

    uid = db.Column("id", db.Integer, primary_key=True)
    account_uid = db.Column("contasfin_id_fk", db.Integer, nullable=False)
    user_uid = db.Column("users_id_fk", db.Integer, nullable=False)
    movements = db.Column("mov_ctfin", db.Integer, nullable=False, default=1)
    payables = db.Column("contaspg", db.Integer, nullable=False, default=1)
    transfers = db.Column("trf_ctfin", db.Integer, nullable=False, default=1)

    def to_dict(self):
        return {
            "account_uid": str(self.account_uid), "movements": self.movements == 2,
            "payables": self.payables == 2, "transfers": self.transfers == 2,
        }
