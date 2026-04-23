"""add barcode to products

Revision ID: 9b1f0f6f2c3a
Revises: 2f6c8eb6ef67
Create Date: 2026-03-31 06:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9b1f0f6f2c3a"
down_revision: Union[str, Sequence[str], None] = "2f6c8eb6ef67"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("products", sa.Column("barcode", sa.String(length=255), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("products", "barcode")
