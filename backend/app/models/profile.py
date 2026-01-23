"""
User profile model.

Maps to the public.profiles table in Supabase which stores user roles
and is automatically synced from auth.users via trigger.
"""

from sqlalchemy import Column, DateTime, Enum, String, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.models import Base
from app.models.enums import UserRole


class Profile(Base):
    """User profile with role information."""

    __tablename__ = "profiles"

    id = Column(PG_UUID(as_uuid=True), primary_key=True)
    email = Column(String, nullable=False)
    role = Column(Enum(UserRole, native_enum=False), nullable=False, default=UserRole.MEMBER)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
