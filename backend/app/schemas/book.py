"""
Pydantic schemas for Book API endpoints.

Defines request and response models for book operations.
"""

from datetime import datetime

from pydantic import BaseModel, Field

from app.core.constants import (
    BOOK_AUTHOR_MAX_LENGTH,
    BOOK_FIELD_MIN_LENGTH,
    BOOK_ISBN_MAX_LENGTH,
    BOOK_TITLE_MAX_LENGTH,
)
from app.models.enums import BookStatus


class BookCreate(BaseModel):
    """Schema for creating a new book."""

    title: str = Field(..., min_length=BOOK_FIELD_MIN_LENGTH, max_length=BOOK_TITLE_MAX_LENGTH)
    author: str = Field(..., min_length=BOOK_FIELD_MIN_LENGTH, max_length=BOOK_AUTHOR_MAX_LENGTH)
    isbn: str | None = Field(None, max_length=BOOK_ISBN_MAX_LENGTH)


class BookUpdate(BaseModel):
    """Schema for updating an existing book."""

    title: str | None = Field(None, min_length=BOOK_FIELD_MIN_LENGTH, max_length=BOOK_TITLE_MAX_LENGTH)
    author: str | None = Field(None, min_length=BOOK_FIELD_MIN_LENGTH, max_length=BOOK_AUTHOR_MAX_LENGTH)
    isbn: str | None = Field(None, max_length=BOOK_ISBN_MAX_LENGTH)
    status: BookStatus | None = None


class BookResponse(BaseModel):
    """Schema for book response."""

    id: int
    title: str
    author: str
    isbn: str | None
    status: BookStatus
    created_at: datetime

    model_config = {"from_attributes": True}
