"""Store ICMS/PIS/COFINS item references as UUID strings.

Revision ID: a4c7e2f91b6d
Revises: 764ed3109d41
"""

from alembic import op
import sqlalchemy as sa


revision = "a4c7e2f91b6d"
down_revision = "764ed3109d41"
branch_labels = None
depends_on = None


_TABLE_NAME = "product_tax_br_icms_pis_cofins_group"
_ITEM_REFERENCE_COLUMNS = (
    "cfop_sell_same_uf_item_uid_fk",
    "cfop_sell_other_uf_item_uid_fk",
    "cfop_sell_export_item_uid_fk",
    "cfop_buy_same_uf_item_uid_fk",
    "cfop_buy_other_uf_item_uid_fk",
    "cfop_buy_import_item_uid_fk",
)


def upgrade():
    for column_name in _ITEM_REFERENCE_COLUMNS:
        op.alter_column(
            _TABLE_NAME,
            column_name,
            existing_type=sa.Boolean(),
            type_=sa.String(length=36),
            existing_nullable=False,
        )


def downgrade():
    for column_name in _ITEM_REFERENCE_COLUMNS:
        op.alter_column(
            _TABLE_NAME,
            column_name,
            existing_type=sa.String(length=36),
            type_=sa.Boolean(),
            existing_nullable=False,
        )
