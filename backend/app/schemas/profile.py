"""
Pydantic schemas for Profile API endpoints.

Defines response models for user profile operations.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.enums import UserRole


class ProfileResponse(BaseModel):
    """Schema for user profile response."""

    id: UUID
    email: str
    role: UserRole
    created_at: datetime

    model_config = {"from_attributes": True}
