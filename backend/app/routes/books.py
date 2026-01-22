"""
Book API routes.

Handles HTTP endpoints for book CRUD operations.
Delegates business logic to the service layer.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.book import Book
from app.schemas.book import BookCreate, BookResponse
from app.services import book_service

router = APIRouter(prefix="/books", tags=["books"])


@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(
    book_data: BookCreate,
    db: AsyncSession = Depends(get_db),
) -> Book:
    """
    Create a new book in the library.

    Args:
        book_data: Book creation data (title, author, isbn)
        db: Database session

    Returns:
        Created book with id, status, and created_at
    """
    return await book_service.create_book(db, book_data)
