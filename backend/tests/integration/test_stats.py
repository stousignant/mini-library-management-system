import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.book import Book
from app.models.enums import BookStatus


@pytest.mark.asyncio
async def test_get_book_statistics_with_mixed_books(async_session: AsyncSession, client: AsyncClient):
    """Test statistics endpoint returns correct counts with mixed book statuses."""
    book1 = Book(
        title="Available Book 1",
        author="Author 1",
        isbn="1111111111",
        status=BookStatus.AVAILABLE,
    )
    book2 = Book(
        title="Available Book 2",
        author="Author 2",
        isbn="2222222222",
        status=BookStatus.AVAILABLE,
    )
    book3 = Book(
        title="Borrowed Book",
        author="Author 3",
        isbn="3333333333",
        status=BookStatus.BORROWED,
    )
    async_session.add_all([book1, book2, book3])
    await async_session.commit()

    response = await client.get("/books/stats")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert data["available"] == 2
    assert data["borrowed"] == 1


@pytest.mark.asyncio
async def test_get_book_statistics_empty_database(client: AsyncClient):
    """Test statistics endpoint handles empty database correctly."""
    response = await client.get("/books/stats")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["available"] == 0
    assert data["borrowed"] == 0


@pytest.mark.asyncio
async def test_get_book_statistics_all_available(async_session: AsyncSession, client: AsyncClient):
    """Test statistics endpoint with all books available."""
    book1 = Book(
        title="Book 1",
        author="Author 1",
        isbn="1111111111",
        status=BookStatus.AVAILABLE,
    )
    book2 = Book(
        title="Book 2",
        author="Author 2",
        isbn="2222222222",
        status=BookStatus.AVAILABLE,
    )
    async_session.add_all([book1, book2])
    await async_session.commit()

    response = await client.get("/books/stats")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert data["available"] == 2
    assert data["borrowed"] == 0


@pytest.mark.asyncio
async def test_get_book_statistics_all_borrowed(async_session: AsyncSession, client: AsyncClient):
    """Test statistics endpoint with all books borrowed."""
    book1 = Book(
        title="Book 1",
        author="Author 1",
        isbn="1111111111",
        status=BookStatus.BORROWED,
    )
    book2 = Book(
        title="Book 2",
        author="Author 2",
        isbn="2222222222",
        status=BookStatus.BORROWED,
    )
    async_session.add_all([book1, book2])
    await async_session.commit()

    response = await client.get("/books/stats")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert data["available"] == 0
    assert data["borrowed"] == 2
