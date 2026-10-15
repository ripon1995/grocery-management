"""backfill price_observation from grocery

Revision ID: c9d2e4f6a8b1
Revises: 842a9bfd3185
Create Date: 2026-10-15 13:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c9d2e4f6a8b1'
down_revision: Union[str, Sequence[str], None] = '842a9bfd3185'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade data."""
    # one manual observation per existing grocery, from its current price/seller,
    # so price history starts with what the app already knows
    op.execute("""
        INSERT INTO price_observation (id, grocery_id, seller, price, source, observed_at, created_at, updated_at)
        SELECT gen_random_uuid(), id, current_seller, current_price, 'MANUAL', updated_at, now(), now()
        FROM grocery
    """)


def downgrade() -> None:
    """Downgrade data."""
    op.execute("DELETE FROM price_observation WHERE source = 'MANUAL'")
