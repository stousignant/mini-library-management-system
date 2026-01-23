"""
Integration tests for user profile endpoints.

Tests the /profile endpoint for retrieving current user information.
"""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient
from jose import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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


@pytest.mark.asyncio
async def test_get_current_user_profile_success(client: AsyncClient, async_session: AsyncSession):
    """Should return current user profile with role."""
    user_id = uuid.uuid4()
    profile = Profile(id=user_id, email="test@example.com", role=UserRole.ADMIN)
    async_session.add(profile)
    await async_session.commit()

    token = create_test_token(str(user_id), "test@example.com", role="service_role")
    response = await client.get("/profile", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(user_id)
    assert data["email"] == "test@example.com"
    assert data["role"] == "ADMIN"


@pytest.mark.asyncio
async def test_get_current_user_profile_member_role(client: AsyncClient, async_session: AsyncSession):
    """Should return current user profile with MEMBER role."""
    user_id = uuid.uuid4()
    profile = Profile(id=user_id, email="member@example.com", role=UserRole.MEMBER)
    async_session.add(profile)
    await async_session.commit()

    token = create_test_token(str(user_id), "member@example.com")
    response = await client.get("/profile", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(user_id)
    assert data["email"] == "member@example.com"
    assert data["role"] == "MEMBER"


@pytest.mark.asyncio
async def test_get_current_user_profile_unauthenticated(client: AsyncClient):
    """Should return 401 when user is not authenticated."""
    response = await client.get("/profile")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_profile_invalid_token(client: AsyncClient):
    """Should return 401 when token is invalid."""
    response = await client.get("/profile", headers={"Authorization": "Bearer invalid_token"})

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_profile_auto_creates_if_not_exists(client: AsyncClient, async_session: AsyncSession):
    """Should auto-create profile with MEMBER role when user profile doesn't exist."""
    user_id = uuid.uuid4()
    email = "newuser@example.com"
    token = create_test_token(str(user_id), email)

    response = await client.get("/profile", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(user_id)
    assert data["email"] == email
    assert data["role"] == "MEMBER"

    # Verify profile was created in database
    result = await async_session.execute(select(Profile).where(Profile.id == user_id))
    profile = result.scalar_one_or_none()
    assert profile is not None
    assert profile.email == email
    assert profile.role == UserRole.MEMBER
