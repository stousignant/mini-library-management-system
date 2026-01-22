"""
SQLAlchemy Book model.

Defines the database schema for books in the library system.
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import (
    BOOK_AUTHOR_MAX_LENGTH,
    BOOK_ISBN_MAX_LENGTH,
    BOOK_TITLE_MAX_LENGTH,
)
from app.models import Base
from app.models.enums import BookStatus


class Book(Base):
    """Book entity in the library system."""

    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(BOOK_TITLE_MAX_LENGTH), nullable=False)
    author: Mapped[str] = mapped_column(String(BOOK_AUTHOR_MAX_LENGTH), nullable=False)
    isbn: Mapped[str | None] = mapped_column(String(BOOK_ISBN_MAX_LENGTH), nullable=True)
    status: Mapped[BookStatus] = mapped_column(
        Enum(BookStatus, native_enum=False),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
