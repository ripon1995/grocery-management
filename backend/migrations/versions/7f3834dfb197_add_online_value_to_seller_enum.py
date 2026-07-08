"""add online value to seller enum

Revision ID: 7f3834dfb197
Revises: 03bba699f6d6
Create Date: 2026-07-08 22:45:42.367369

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7f3834dfb197'
down_revision: Union[str, Sequence[str], None] = '03bba699f6d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TYPE seller ADD VALUE IF NOT EXISTS 'ONLINE'")


def downgrade() -> None:
    """Downgrade schema."""
    # Postgres does not support removing a value from an enum type;
    # doing so requires recreating the type, which is skipped here.
    pass
