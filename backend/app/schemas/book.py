"""
Pydantic schemas for Book API endpoints.

Defines request and response models for book operations.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.core.constants import (
    BOOK_AUTHOR_MAX_LENGTH,
    BOOK_COVER_IMAGE_MAX_LENGTH,
    BOOK_FIELD_MIN_LENGTH,
    BOOK_ISBN_MAX_LENGTH,
    BOOK_SUMMARY_MAX_LENGTH,
    BOOK_TITLE_MAX_LENGTH,
)
from app.models.enums import BookStatus


class BookCreate(BaseModel):
    """Schema for creating a new book."""

    title: str = Field(..., min_length=BOOK_FIELD_MIN_LENGTH, max_length=BOOK_TITLE_MAX_LENGTH)
    author: str = Field(..., min_length=BOOK_FIELD_MIN_LENGTH, max_length=BOOK_AUTHOR_MAX_LENGTH)
    isbn: str | None = Field(None, max_length=BOOK_ISBN_MAX_LENGTH)
    cover_image: str | None = Field(None, max_length=BOOK_COVER_IMAGE_MAX_LENGTH)
    summary: str | None = Field(None, max_length=BOOK_SUMMARY_MAX_LENGTH)


class BookUpdate(BaseModel):
    """Schema for updating an existing book."""

    title: str | None = Field(None, min_length=BOOK_FIELD_MIN_LENGTH, max_length=BOOK_TITLE_MAX_LENGTH)
    author: str | None = Field(None, min_length=BOOK_FIELD_MIN_LENGTH, max_length=BOOK_AUTHOR_MAX_LENGTH)
    isbn: str | None = Field(None, max_length=BOOK_ISBN_MAX_LENGTH)
    cover_image: str | None = Field(None, max_length=BOOK_COVER_IMAGE_MAX_LENGTH)
    summary: str | None = Field(None, max_length=BOOK_SUMMARY_MAX_LENGTH)
    status: BookStatus | None = None


class BookResponse(BaseModel):
    """Schema for book response."""

    id: int
    title: str
    author: str
    isbn: str | None
    cover_image: str | None
    summary: str | None
    status: BookStatus
    borrowed_by: UUID | None
    created_at: datetime

    model_config = {"from_attributes": True}
