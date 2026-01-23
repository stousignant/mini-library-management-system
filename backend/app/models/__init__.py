"""
SQLAlchemy models package.

Exports the Base declarative class and all model entities.
"""

from sqlalchemy.orm import DeclarativeBase

from app.models.enums import UserRole
from app.models.profile import Profile


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


__all__ = ["Base", "Profile", "UserRole"]
