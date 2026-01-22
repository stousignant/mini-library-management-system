"""
Book API routes.

Handles CRUD operations for books in the library system.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import DEFAULT_BOOK_STATUS
from app.core.database import get_db
from app.models.book import Book
from app.schemas.book import BookCreate, BookResponse

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
    book = Book(
        title=book_data.title,
        author=book_data.author,
        isbn=book_data.isbn,
        status=DEFAULT_BOOK_STATUS,
    )

    db.add(book)
    await db.commit()
    await db.refresh(book)

    return book
