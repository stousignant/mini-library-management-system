"""
SQLAlchemy Book model.

Defines the database schema for books in the library system.
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.models.enums import BookStatus


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


class Book(Base):
    """Book entity in the library system."""

    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    author: Mapped[str] = mapped_column(String(255), nullable=False)
    isbn: Mapped[str | None] = mapped_column(String(20), nullable=True)
    status: Mapped[BookStatus] = mapped_column(
        Enum(BookStatus, native_enum=False),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
