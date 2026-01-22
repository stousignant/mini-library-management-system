"""
Book service layer.

Handles business logic and database operations for books.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import DEFAULT_BOOK_STATUS
from app.models.book import Book
from app.schemas.book import BookCreate, BookUpdate


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
        cover_image=book_data.cover_image,
        summary=book_data.summary,
        status=DEFAULT_BOOK_STATUS,
    )

    db.add(book)
    await db.commit()
    await db.refresh(book)

    return book


async def get_book_by_id(db: AsyncSession, book_id: int) -> Book | None:
    """
    Retrieve a book by its ID.

    Args:
        db: Database session
        book_id: ID of the book to retrieve

    Returns:
        Book entity if found, None otherwise
    """
    result = await db.execute(select(Book).where(Book.id == book_id))
    return result.scalar_one_or_none()


async def get_all_books(db: AsyncSession) -> list[Book]:
    """
    Retrieve all books from the database.

    Args:
        db: Database session

    Returns:
        List of all book entities
    """
    result = await db.execute(select(Book))
    return list(result.scalars().all())


async def update_book(db: AsyncSession, book_id: int, book_data: BookUpdate) -> Book | None:
    """
    Update an existing book.

    Args:
        db: Database session
        book_id: ID of the book to update
        book_data: Updated book data

    Returns:
        Updated book entity if found, None otherwise
    """
    book = await get_book_by_id(db, book_id)
    if book is None:
        return None

    update_values = book_data.model_dump(exclude_unset=True)
    for field, value in update_values.items():
        setattr(book, field, value)

    await db.commit()
    await db.refresh(book)

    return book


async def delete_book(db: AsyncSession, book_id: int) -> bool:
    """
    Delete a book by its ID.

    Args:
        db: Database session
        book_id: ID of the book to delete

    Returns:
        True if book was deleted, False if not found
    """
    book = await get_book_by_id(db, book_id)
    if book is None:
        return False

    await db.delete(book)
    await db.commit()

    return True
