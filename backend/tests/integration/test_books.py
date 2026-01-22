"""
Integration tests for Book CRUD endpoints.

Tests the /books/ API endpoints with real database interactions.
"""

import pytest


@pytest.mark.asyncio
async def test_create_book(client):
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
    response = await client.post("/books/", json=payload)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["title"] == payload["title"]
    assert data["author"] == payload["author"]
    assert data["isbn"] == payload["isbn"]
    assert data["status"] == "AVAILABLE"
    assert "created_at" in data


@pytest.mark.asyncio
async def test_get_book_by_id(client):
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
    create_response = await client.post("/books/", json=create_payload)
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
