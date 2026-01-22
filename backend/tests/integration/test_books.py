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
