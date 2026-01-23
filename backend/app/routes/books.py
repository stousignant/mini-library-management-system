"""
Book API routes.

Handles HTTP endpoints for book CRUD operations.
Delegates business logic to the service layer.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user_with_role, require_role
from app.models.book import Book
from app.models.enums import UserRole
from app.models.profile import Profile
from app.schemas.book import BookCreate, BookResponse, BookStatistics, BookUpdate
from app.services import book_service

router = APIRouter(prefix="/books", tags=["books"])


@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(
    book_data: BookCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Profile = Depends(require_role(UserRole.ADMIN)),
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


@router.get("/", response_model=list[BookResponse], status_code=status.HTTP_200_OK)
async def list_books(
    db: AsyncSession = Depends(get_db),
) -> list[Book]:
    """
    Retrieve all books from the library.

    Args:
        db: Database session

    Returns:
        List of all books
    """
    return await book_service.get_all_books(db)


@router.get("/stats", response_model=BookStatistics, status_code=status.HTTP_200_OK)
async def get_book_statistics(
    db: AsyncSession = Depends(get_db),
) -> BookStatistics:
    """
    Get book statistics including total count, available, and borrowed.

    Args:
        db: Database session

    Returns:
        BookStatistics with total, available, and borrowed counts
    """
    return await book_service.get_book_statistics(db)


@router.get("/{book_id}", response_model=BookResponse, status_code=status.HTTP_200_OK)
async def get_book(
    book_id: int,
    db: AsyncSession = Depends(get_db),
) -> Book:
    """
    Retrieve a book by its ID.

    Args:
        book_id: ID of the book to retrieve
        db: Database session

    Returns:
        Book entity if found

    Raises:
        HTTPException: 404 if book not found
    """
    book = await book_service.get_book_by_id(db, book_id)
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found",
        )
    return book


@router.put("/{book_id}", response_model=BookResponse, status_code=status.HTTP_200_OK)
async def update_book(
    book_id: int,
    book_data: BookUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Profile = Depends(require_role(UserRole.ADMIN)),
) -> Book:
    """
    Update a book by its ID.

    Args:
        book_id: ID of the book to update
        book_data: Updated book data
        db: Database session

    Returns:
        Updated book entity

    Raises:
        HTTPException: 404 if book not found
    """
    book = await book_service.update_book(db, book_id, book_data)
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found",
        )
    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Profile = Depends(require_role(UserRole.ADMIN)),
) -> None:
    """
    Delete a book by its ID.

    Args:
        book_id: ID of the book to delete
        db: Database session

    Returns:
        None (204 No Content on success)

    Raises:
        HTTPException: 404 if book not found
    """
    deleted = await book_service.delete_book(db, book_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found",
        )
    return None


@router.patch("/{book_id}/borrow", response_model=BookResponse, status_code=status.HTTP_200_OK)
async def borrow_book(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Profile = Depends(get_current_user_with_role),
) -> Book:
    """
    Mark a book as borrowed by the authenticated user.

    Args:
        book_id: ID of the book to borrow
        db: Database session
        current_user: Authenticated user profile

    Returns:
        Updated book with borrowed status

    Raises:
        HTTPException: 404 if book not found
        HTTPException: 400 if book is already borrowed
    """
    try:
        book = await book_service.borrow_book(db, book_id, current_user.id)
        if book is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Book with id {book_id} not found",
            )
        return book
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.patch("/{book_id}/return", response_model=BookResponse, status_code=status.HTTP_200_OK)
async def return_book(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Profile = Depends(get_current_user_with_role),
) -> Book:
    """
    Mark a book as returned (available).

    Users can only return books they borrowed. Admins can return any book.

    Args:
        book_id: ID of the book to return
        db: Database session
        current_user: Authenticated user profile

    Returns:
        Updated book with available status

    Raises:
        HTTPException: 404 if book not found
        HTTPException: 400 if book is not borrowed or user is not the borrower
    """
    try:
        user_id_to_check = None if current_user.role == UserRole.ADMIN else current_user.id
        book = await book_service.return_book(db, book_id, user_id_to_check)
        if book is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Book with id {book_id} not found",
            )
        return book
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
