"""
Pydantic schemas for Book API endpoints.

Defines request and response models for book operations.
"""

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import BookStatus


class BookCreate(BaseModel):
    """Schema for creating a new book."""

    title: str = Field(..., min_length=1, max_length=255)
    author: str = Field(..., min_length=1, max_length=255)
    isbn: str | None = Field(None, max_length=20)


class BookResponse(BaseModel):
    """Schema for book response."""

    id: int
    title: str
    author: str
    isbn: str | None
    status: BookStatus
    created_at: datetime

    model_config = {"from_attributes": True}
