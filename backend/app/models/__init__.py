"""
SQLAlchemy models package.

Exports the Base declarative class and all model entities.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass
