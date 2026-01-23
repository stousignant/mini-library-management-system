"""Integration tests for book API authentication and authorization."""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient
from jose import jwt

from app.core.config import get_settings
from app.core.constants import JWT_ALGORITHM, JWT_AUDIENCE_AUTHENTICATED
from app.models.enums import UserRole
from app.models.profile import Profile

settings = get_settings()


def create_test_token(
    user_id: str, email: str, role: str = "authenticated", expires_delta: timedelta | None = None
) -> str:
    """Create test JWT token with optional role."""
    if expires_delta is None:
        expires_delta = timedelta(hours=1)

    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "aud": JWT_AUDIENCE_AUTHENTICATED,
        "exp": datetime.now(timezone.utc) + expires_delta,
        "iat": datetime.now(timezone.utc),
    }

    return jwt.encode(payload, settings.supabase_jwt_secret, algorithm=JWT_ALGORITHM)


@pytest.fixture
async def admin_profile(async_session):
    """Create admin user profile."""
    user_id = uuid.uuid4()
    profile = Profile(
        id=user_id,
        email="admin@example.com",
        role=UserRole.ADMIN,
        created_at=datetime.now(timezone.utc),
    )
    async_session.add(profile)
    await async_session.commit()
    return profile


@pytest.fixture
async def member_profile(async_session):
    """Create member user profile."""
    user_id = uuid.uuid4()
    profile = Profile(
        id=user_id,
        email="member@example.com",
        role=UserRole.MEMBER,
        created_at=datetime.now(timezone.utc),
    )
    async_session.add(profile)
    await async_session.commit()
    return profile


@pytest.fixture
def admin_token(admin_profile):
    """Generate token for admin user."""
    return create_test_token(str(admin_profile.id), admin_profile.email, role="service_role")


@pytest.fixture
def member_token(member_profile):
    """Generate token for member user."""
    return create_test_token(str(member_profile.id), member_profile.email, role="authenticated")


class TestBooksAuthIntegration:
    """Integration tests for books API with authentication."""

    async def test_get_books_public_no_auth_required(self, client: AsyncClient):
        """GET /books should work without authentication."""
        response = await client.get("/books/")

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_create_book_requires_auth(self, client: AsyncClient):
        """POST /books should return 401 without token."""
        book_data = {
            "title": "Test Book",
            "author": "Test Author",
            "isbn": "1234567890",
        }

        response = await client.post("/books/", json=book_data)

        assert response.status_code == 401  # HTTPBearer returns 401 when no token

    async def test_create_book_requires_admin(self, client: AsyncClient, admin_token: str):
        """POST /books should succeed for admin user."""
        book_data = {
            "title": "Admin Book",
            "author": "Admin Author",
            "isbn": "1234567890",
        }

        response = await client.post(
            "/books/",
            json=book_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Admin Book"
        assert data["author"] == "Admin Author"

    async def test_create_book_forbidden_for_member(self, client: AsyncClient, member_token: str):
        """POST /books should return 403 for member user."""
        book_data = {
            "title": "Member Book",
            "author": "Member Author",
            "isbn": "1234567890",
        }

        response = await client.post(
            "/books/",
            json=book_data,
            headers={"Authorization": f"Bearer {member_token}"},
        )

        assert response.status_code == 403
        assert "Insufficient permissions" in response.json()["detail"]

    async def test_update_book_requires_admin(self, client: AsyncClient, admin_token: str):
        """PUT /books/{id} should succeed for admin user."""
        # First create a book as admin
        book_data = {"title": "Original Title", "author": "Original Author", "isbn": "1234567890"}
        create_response = await client.post(
            "/books/",
            json=book_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        book_id = create_response.json()["id"]

        # Update the book
        update_data = {"title": "Updated Title"}
        response = await client.put(
            f"/books/{book_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["author"] == "Original Author"

    async def test_update_book_forbidden_for_member(self, client: AsyncClient, admin_token: str, member_token: str):
        """PUT /books/{id} should return 403 for member user."""
        # Create book as admin
        book_data = {"title": "Test Book", "author": "Test Author", "isbn": "1234567890"}
        create_response = await client.post(
            "/books/",
            json=book_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        book_id = create_response.json()["id"]

        # Try to update as member
        update_data = {"title": "Hacked Title"}
        response = await client.put(
            f"/books/{book_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {member_token}"},
        )

        assert response.status_code == 403
        assert "Insufficient permissions" in response.json()["detail"]

    async def test_delete_book_requires_admin(self, client: AsyncClient, admin_token: str):
        """DELETE /books/{id} should succeed for admin user."""
        # Create book as admin
        book_data = {"title": "To Delete", "author": "Test Author", "isbn": "1234567890"}
        create_response = await client.post(
            "/books/",
            json=book_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        book_id = create_response.json()["id"]

        # Delete the book
        response = await client.delete(
            f"/books/{book_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == 204

        # Verify book is deleted
        get_response = await client.get(f"/books/{book_id}")
        assert get_response.status_code == 404

    async def test_delete_book_forbidden_for_member(self, client: AsyncClient, admin_token: str, member_token: str):
        """DELETE /books/{id} should return 403 for member user."""
        # Create book as admin
        book_data = {"title": "Protected Book", "author": "Test Author", "isbn": "1234567890"}
        create_response = await client.post(
            "/books/",
            json=book_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        book_id = create_response.json()["id"]

        # Try to delete as member
        response = await client.delete(
            f"/books/{book_id}",
            headers={"Authorization": f"Bearer {member_token}"},
        )

        assert response.status_code == 403
        assert "Insufficient permissions" in response.json()["detail"]

    async def test_invalid_token_returns_401(self, client: AsyncClient):
        """Invalid token should return 401."""
        book_data = {"title": "Test", "author": "Test", "isbn": "1234567890"}

        response = await client.post(
            "/books/",
            json=book_data,
            headers={"Authorization": "Bearer invalid.token.here"},
        )

        assert response.status_code == 401
        assert "Could not validate credentials" in response.json()["detail"]

    async def test_member_can_borrow_available_book(self, client: AsyncClient, admin_token: str, member_token: str):
        """PATCH /books/{id}/borrow should allow member to borrow available book."""
        # Create book as admin
        book_data = {"title": "Borrowable Book", "author": "Test Author", "isbn": "1234567890"}
        create_response = await client.post(
            "/books/",
            json=book_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        book_id = create_response.json()["id"]

        # Member borrows the book
        response = await client.patch(
            f"/books/{book_id}/borrow",
            headers={"Authorization": f"Bearer {member_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "BORROWED"

    async def test_member_can_return_borrowed_book(self, client: AsyncClient, admin_token: str, member_token: str):
        """PATCH /books/{id}/return should allow member to return borrowed book."""
        # Create and borrow book
        book_data = {"title": "Returnable Book", "author": "Test Author", "isbn": "1234567890"}
        create_response = await client.post(
            "/books/",
            json=book_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        book_id = create_response.json()["id"]

        await client.patch(
            f"/books/{book_id}/borrow",
            headers={"Authorization": f"Bearer {member_token}"},
        )

        # Member returns the book
        response = await client.patch(
            f"/books/{book_id}/return",
            headers={"Authorization": f"Bearer {member_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "AVAILABLE"

    async def test_borrow_already_borrowed_book_fails(self, client: AsyncClient, admin_token: str, member_token: str):
        """Borrowing already borrowed book should return 400."""
        # Create and borrow book
        book_data = {"title": "Already Borrowed", "author": "Test Author", "isbn": "1234567890"}
        create_response = await client.post(
            "/books/",
            json=book_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        book_id = create_response.json()["id"]

        await client.patch(
            f"/books/{book_id}/borrow",
            headers={"Authorization": f"Bearer {member_token}"},
        )

        # Try to borrow again
        response = await client.patch(
            f"/books/{book_id}/borrow",
            headers={"Authorization": f"Bearer {member_token}"},
        )

        assert response.status_code == 400
        assert "already borrowed" in response.json()["detail"].lower()

    async def test_return_available_book_fails(self, client: AsyncClient, admin_token: str, member_token: str):
        """Returning available book should return 400."""
        # Create book (available by default)
        book_data = {"title": "Available Book", "author": "Test Author", "isbn": "1234567890"}
        create_response = await client.post(
            "/books/",
            json=book_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        book_id = create_response.json()["id"]

        # Try to return an available book
        response = await client.patch(
            f"/books/{book_id}/return",
            headers={"Authorization": f"Bearer {member_token}"},
        )

        assert response.status_code == 400
        assert "not borrowed" in response.json()["detail"].lower()

    async def test_borrow_requires_authentication(self, client: AsyncClient, admin_token: str):
        """PATCH /books/{id}/borrow should require authentication."""
        # Create book as admin
        book_data = {"title": "Auth Required", "author": "Test Author", "isbn": "1234567890"}
        create_response = await client.post(
            "/books/",
            json=book_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        book_id = create_response.json()["id"]

        # Try to borrow without token
        response = await client.patch(f"/books/{book_id}/borrow")

        assert response.status_code == 401
