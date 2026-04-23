from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'fix_safety_level'
down_revision = 'c1c42e364659'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # создаём enum type
    safety_enum = sa.Enum('safe', 'caution', 'danger', "unknown", name='safety_level_enum')
    safety_enum.create(op.get_bind(), checkfirst=True)

    # добавляем колонку
    op.add_column(
        'ingredients',
        sa.Column(
            'safety_level',
            safety_enum,
            nullable=False,
            server_default='unknown'
        )
    )

def downgrade() -> None:
    op.drop_column('ingredients', 'safety_level')
    safety_enum = sa.Enum('safe', 'caution', 'danger', 'unknown', name='safety_level_enum')
    safety_enum.drop(op.get_bind(), checkfirst=True)
