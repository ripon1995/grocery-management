"""add category column to grocery

Revision ID: 5dc40e0c9376
Revises: 7f3834dfb197
Create Date: 2026-07-11 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5dc40e0c9376'
down_revision: Union[str, Sequence[str], None] = '7f3834dfb197'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    grocery_category_enum = sa.Enum(
        'TOILETRIES', 'FOOD', 'COOKIES', 'OIL', 'OTHER',
        name='grocerycategory'
    )
    grocery_category_enum.create(op.get_bind(), checkfirst=True)
    op.add_column(
        'grocery',
        sa.Column(
            'category',
            grocery_category_enum,
            nullable=False,
            server_default='OTHER'
        )
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('grocery', 'category')
    sa.Enum(name='grocerycategory').drop(op.get_bind(), checkfirst=True)
