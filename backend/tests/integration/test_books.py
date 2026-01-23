"""
Integration tests for Book CRUD endpoints.

Tests the /books/ API endpoints with real database interactions.
"""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt

from app.core.config import get_settings
from app.core.constants import JWT_ALGORITHM, JWT_AUDIENCE_AUTHENTICATED
from app.models.enums import UserRole
from app.models.profile import Profile

settings = get_settings()


def create_test_token(user_id: str, email: str) -> str:
    """Create test JWT token."""
    payload = {
        "sub": user_id,
        "email": email,
        "aud": JWT_AUDIENCE_AUTHENTICATED,
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.supabase_jwt_secret, algorithm=JWT_ALGORITHM)


@pytest.fixture
async def admin_profile(async_session):
    """Create admin user profile for tests."""
    user_id = uuid.uuid4()
    profile = Profile(
        id=user_id,
        email="admin@test.com",
        role=UserRole.ADMIN,
        created_at=datetime.now(timezone.utc),
    )
    async_session.add(profile)
    await async_session.commit()
    return profile


@pytest.fixture
def admin_token(admin_profile):
    """Generate token for admin user."""
    return create_test_token(str(admin_profile.id), admin_profile.email)


@pytest.mark.asyncio
async def test_create_book(client, admin_token):
    """
    Test creating a new book via POST /books/.

    Given: Valid book data (title, author, isbn)
    When: POST request is made to /books/
    Then: Book is created with status 201
    And: Response contains id, all book fields, and status=AVAILABLE
    """
    # Arrange
    payload = {
        "title": "The Pragmatic Programmer",
        "author": "Andrew Hunt",
        "isbn": "978-0201616224",
    }

    # Act
    response = await client.post("/books/", json=payload, headers={"Authorization": f"Bearer {admin_token}"})

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["title"] == payload["title"]
    assert data["author"] == payload["author"]
    assert data["isbn"] == payload["isbn"]
    assert data["cover_image"] is None
    assert data["summary"] is None
    assert data["status"] == "AVAILABLE"
    assert "created_at" in data


@pytest.mark.asyncio
async def test_get_book_by_id(client, admin_token):
    """
    Test retrieving a single book by ID via GET /books/{id}.

    Given: A book exists in the database
    When: GET request is made to /books/{id}
    Then: Book is retrieved with status 200
    And: Response contains all book fields
    """
    # Arrange - Create a book first
    create_payload = {
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "isbn": "978-0132350884",
    }
    create_response = await client.post(
        "/books/", json=create_payload, headers={"Authorization": f"Bearer {admin_token}"}
    )
    created_book = create_response.json()
    book_id = created_book["id"]

    # Act
    response = await client.get(f"/books/{book_id}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == book_id
    assert data["title"] == create_payload["title"]
    assert data["author"] == create_payload["author"]
    assert data["isbn"] == create_payload["isbn"]
    assert data["status"] == "AVAILABLE"
    assert "created_at" in data


@pytest.mark.asyncio
async def test_list_all_books(client, admin_token):
    """
    Test retrieving all books via GET /books/.

    Given: Multiple books exist in the database
    When: GET request is made to /books/
    Then: All books are retrieved with status 200
    And: Response is a list containing all books
    """
    # Arrange - Create multiple books
    books_data = [
        {"title": "Clean Code", "author": "Robert C. Martin", "isbn": "978-0132350884"},
        {"title": "Refactoring", "author": "Martin Fowler", "isbn": "978-0134757599"},
        {"title": "Design Patterns", "author": "Gang of Four", "isbn": "978-0201633610"},
    ]

    for book_data in books_data:
        await client.post("/books/", json=book_data, headers={"Authorization": f"Bearer {admin_token}"})

    # Act
    response = await client.get("/books/")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3
    assert all("id" in book for book in data)
    assert all("title" in book for book in data)
    assert all("status" in book for book in data)


@pytest.mark.asyncio
async def test_update_book(client, admin_token):
    """
    Test updating a book via PUT /books/{id}.

    Given: A book exists in the database
    When: PUT request is made with updated data
    Then: Book is updated with status 200
    And: Response contains updated book fields
    """
    # Arrange - Create a book first
    create_payload = {
        "title": "Original Title",
        "author": "Original Author",
        "isbn": "978-0000000000",
    }
    create_response = await client.post(
        "/books/", json=create_payload, headers={"Authorization": f"Bearer {admin_token}"}
    )
    created_book = create_response.json()
    book_id = created_book["id"]

    # Act - Update the book
    update_payload = {
        "title": "Updated Title",
        "author": "Updated Author",
        "isbn": "978-1111111111",
    }
    response = await client.put(
        f"/books/{book_id}", json=update_payload, headers={"Authorization": f"Bearer {admin_token}"}
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == book_id
    assert data["title"] == update_payload["title"]
    assert data["author"] == update_payload["author"]
    assert data["isbn"] == update_payload["isbn"]
    assert data["status"] == "AVAILABLE"
    assert "created_at" in data


@pytest.mark.asyncio
async def test_update_book_status(client, admin_token):
    """
    Test updating a book's status via PUT /books/{id}.

    Given: A book exists with status AVAILABLE
    When: PUT request is made with status BORROWED
    Then: Book status is updated with status 200
    And: Response contains updated status
    """
    # Arrange - Create a book first
    create_payload = {
        "title": "Book to Borrow",
        "author": "Test Author",
        "isbn": "978-0000000000",
    }
    create_response = await client.post(
        "/books/", json=create_payload, headers={"Authorization": f"Bearer {admin_token}"}
    )
    created_book = create_response.json()
    book_id = created_book["id"]
    assert created_book["status"] == "AVAILABLE"

    # Act - Update status to BORROWED
    update_payload = {"status": "BORROWED"}
    response = await client.put(
        f"/books/{book_id}", json=update_payload, headers={"Authorization": f"Bearer {admin_token}"}
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == book_id
    assert data["status"] == "BORROWED"
    assert data["title"] == create_payload["title"]
    assert data["author"] == create_payload["author"]

    # Act - Update status back to AVAILABLE
    update_payload = {"status": "AVAILABLE"}
    response = await client.put(
        f"/books/{book_id}", json=update_payload, headers={"Authorization": f"Bearer {admin_token}"}
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "AVAILABLE"


@pytest.mark.asyncio
async def test_create_book_with_cover_and_summary(client, admin_token):
    """
    Test creating a book with cover_image and summary fields.

    Given: Valid book data including cover_image and summary
    When: POST request is made to /books/
    Then: Book is created with status 201
    And: Response contains cover_image and summary fields
    """
    # Arrange
    payload = {
        "title": "Domain-Driven Design",
        "author": "Eric Evans",
        "isbn": "978-0321125217",
        "cover_image": "https://covers.openlibrary.org/b/id/12345-L.jpg",
        "summary": "Published by Addison-Wesley",
    }

    # Act
    response = await client.post("/books/", json=payload, headers={"Authorization": f"Bearer {admin_token}"})

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["title"] == payload["title"]
    assert data["author"] == payload["author"]
    assert data["isbn"] == payload["isbn"]
    assert data["cover_image"] == payload["cover_image"]
    assert data["summary"] == payload["summary"]
    assert data["status"] == "AVAILABLE"
    assert "created_at" in data


@pytest.mark.asyncio
async def test_update_book_cover_and_summary(client, admin_token):
    """
    Test updating a book's cover_image and summary fields.

    Given: A book exists without cover_image and summary
    When: PUT request is made with cover_image and summary
    Then: Book is updated with status 200
    And: Response contains updated fields
    """
    # Arrange - Create a book without cover_image and summary
    create_payload = {
        "title": "Test Book",
        "author": "Test Author",
        "isbn": "978-0000000000",
    }
    create_response = await client.post(
        "/books/", json=create_payload, headers={"Authorization": f"Bearer {admin_token}"}
    )
    created_book = create_response.json()
    book_id = created_book["id"]
    assert created_book["cover_image"] is None
    assert created_book["summary"] is None

    # Act - Update with cover_image and summary
    update_payload = {
        "cover_image": "https://example.com/cover.jpg",
        "summary": "Test summary information",
    }
    response = await client.put(
        f"/books/{book_id}", json=update_payload, headers={"Authorization": f"Bearer {admin_token}"}
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == book_id
    assert data["cover_image"] == update_payload["cover_image"]
    assert data["summary"] == update_payload["summary"]
    assert data["title"] == create_payload["title"]
    assert data["author"] == create_payload["author"]


@pytest.mark.asyncio
async def test_delete_book(client, admin_token):
    """
    Test deleting a book via DELETE /books/{id}.

    Given: A book exists in the database
    When: DELETE request is made to /books/{id}
    Then: Book is deleted with status 204
    And: Subsequent GET request returns 404
    """
    # Arrange - Create a book first
    create_payload = {
        "title": "Book to Delete",
        "author": "Test Author",
        "isbn": "978-0000000000",
    }
    create_response = await client.post(
        "/books/", json=create_payload, headers={"Authorization": f"Bearer {admin_token}"}
    )
    created_book = create_response.json()
    book_id = created_book["id"]

    # Act - Delete the book
    response = await client.delete(f"/books/{book_id}", headers={"Authorization": f"Bearer {admin_token}"})

    # Assert
    assert response.status_code == 204

    # Verify book is deleted
    get_response = await client.get(f"/books/{book_id}")
    assert get_response.status_code == 404
