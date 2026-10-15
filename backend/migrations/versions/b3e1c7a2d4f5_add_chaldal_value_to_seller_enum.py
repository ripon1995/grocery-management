"""add chaldal value to seller enum

Revision ID: b3e1c7a2d4f5
Revises: 41ab5277874e
Create Date: 2026-10-15 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b3e1c7a2d4f5'
down_revision: Union[str, Sequence[str], None] = '41ab5277874e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # kept in its own migration: a value added with ADD VALUE
    # can't be used in the same transaction it was added in
    op.execute("ALTER TYPE seller ADD VALUE IF NOT EXISTS 'CHALDAL'")


def downgrade() -> None:
    """Downgrade schema."""
    # Postgres does not support removing a value from an enum type;
    # doing so requires recreating the type, which is skipped here.
    pass
