"""
SQLAlchemy models package.

Exports the Base declarative class and all model entities.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


from app.models.enums import UserRole  # noqa: E402
from app.models.profile import Profile  # noqa: E402

__all__ = ["Base", "Profile", "UserRole"]
