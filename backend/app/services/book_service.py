"""
Book service layer.

Handles business logic and database operations for books.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import DEFAULT_BOOK_STATUS
from app.models.book import Book
from app.schemas.book import BookCreate


async def create_book(db: AsyncSession, book_data: BookCreate) -> Book:
    """
    Create a new book in the database.

    Args:
        db: Database session
        book_data: Book creation data

    Returns:
        Created book entity
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
