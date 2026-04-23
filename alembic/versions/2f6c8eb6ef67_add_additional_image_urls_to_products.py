"""add additional image urls to products

Revision ID: 2f6c8eb6ef67
Revises: 3edc492da3f9
Create Date: 2026-03-30 22:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '2f6c8eb6ef67'
down_revision: Union[str, Sequence[str], None] = '3edc492da3f9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'products',
        sa.Column(
            'additional_image_urls',
            postgresql.ARRAY(sa.Text()),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('products', 'additional_image_urls')
