"""change book summary to text type

Revision ID: 5f2eba430061
Revises: 883b962a55c2
Create Date: 2026-01-23 14:41:32.374746

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5f2eba430061"
down_revision: Union[str, Sequence[str], None] = "883b962a55c2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: Change summary from VARCHAR(1000) to TEXT."""
    op.alter_column(
        "books",
        "summary",
        type_=sa.Text(),
        existing_type=sa.String(length=1000),
        existing_nullable=True,
    )


def downgrade() -> None:
    """Downgrade schema: Change summary from TEXT back to VARCHAR(1000)."""
    op.alter_column(
        "books",
        "summary",
        type_=sa.String(length=1000),
        existing_type=sa.Text(),
        existing_nullable=True,
    )
