"""add borrowed_by to books

Revision ID: 883b962a55c2
Revises: c9a8f7e4d2b1
Create Date: 2026-01-23 08:12:49.726833

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "883b962a55c2"
down_revision: Union[str, Sequence[str], None] = "c9a8f7e4d2b1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add borrowed_by column to books table."""
    op.add_column("books", sa.Column("borrowed_by", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key("fk_books_borrowed_by_profiles", "books", "profiles", ["borrowed_by"], ["id"])


def downgrade() -> None:
    """Remove borrowed_by column from books table."""
    op.drop_constraint("fk_books_borrowed_by_profiles", "books", type_="foreignkey")
    op.drop_column("books", "borrowed_by")
