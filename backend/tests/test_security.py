"""Tests for authentication and authorization."""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException
from jose import jwt

from app.core.config import get_settings
from app.core.constants import (
    ERROR_INSUFFICIENT_PERMISSIONS,
    ERROR_INVALID_TOKEN,
    JWT_ALGORITHM,
    JWT_AUDIENCE_AUTHENTICATED,
)
from app.core.security import decode_jwt_token, get_current_user, get_current_user_with_role, require_role
from app.models.enums import UserRole

settings = get_settings()


def create_test_jwt_token(
    user_id: str | None = None,
    email: str = "test@example.com",
    audience: str = JWT_AUDIENCE_AUTHENTICATED,
    expires_delta: timedelta | None = None,
) -> str:
    """Helper to create test JWT tokens."""
    if user_id is None:
        user_id = str(uuid.uuid4())

    if expires_delta is None:
        expires_delta = timedelta(hours=1)

    payload = {
        "sub": user_id,
        "email": email,
        "aud": audience,
        "exp": datetime.now(timezone.utc) + expires_delta,
        "iat": datetime.now(timezone.utc),
    }

    return jwt.encode(payload, settings.supabase_jwt_secret, algorithm=JWT_ALGORITHM)


class TestDecodeJwtToken:
    """Tests for decode_jwt_token function."""

    def test_decode_valid_token(self):
        """Should decode a valid JWT token."""
        user_id = str(uuid.uuid4())
        email = "test@example.com"
        token = create_test_jwt_token(user_id=user_id, email=email)

        payload = decode_jwt_token(token)

        assert payload["sub"] == user_id
        assert payload["email"] == email
        assert payload["aud"] == JWT_AUDIENCE_AUTHENTICATED

    def test_decode_invalid_token(self):
        """Should raise HTTPException for invalid token."""
        with pytest.raises(HTTPException) as exc_info:
            decode_jwt_token("invalid.token.here")

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == ERROR_INVALID_TOKEN

    def test_decode_expired_token(self):
        """Should raise HTTPException for expired token."""
        token = create_test_jwt_token(expires_delta=timedelta(seconds=-10))

        with pytest.raises(HTTPException) as exc_info:
            decode_jwt_token(token)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == ERROR_INVALID_TOKEN

    def test_decode_wrong_audience(self):
        """Should raise HTTPException for wrong audience."""
        token = create_test_jwt_token(audience="wrong-audience")

        with pytest.raises(HTTPException) as exc_info:
            decode_jwt_token(token)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == ERROR_INVALID_TOKEN

    def test_decode_wrong_secret(self):
        """Should raise HTTPException when token signed with wrong secret."""
        payload = {
            "sub": str(uuid.uuid4()),
            "email": "test@example.com",
            "aud": JWT_AUDIENCE_AUTHENTICATED,
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        }
        token = jwt.encode(payload, "wrong-secret", algorithm=JWT_ALGORITHM)

        with pytest.raises(HTTPException) as exc_info:
            decode_jwt_token(token)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == ERROR_INVALID_TOKEN


class TestGetCurrentUser:
    """Tests for get_current_user dependency."""

    async def test_get_current_user_valid_token(self):
        """Should return user payload for valid token."""
        from fastapi.security import HTTPAuthorizationCredentials

        user_id = str(uuid.uuid4())
        email = "test@example.com"
        token = create_test_jwt_token(user_id=user_id, email=email)

        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        payload = await get_current_user(credentials)

        assert payload["sub"] == user_id
        assert payload["email"] == email

    async def test_get_current_user_invalid_token(self):
        """Should raise HTTPException for invalid token."""
        from fastapi.security import HTTPAuthorizationCredentials

        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid.token")

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials)

        assert exc_info.value.status_code == 401


class TestGetCurrentUserWithRole:
    """Tests for get_current_user_with_role dependency."""

    async def test_get_user_with_role_existing_profile(self, async_session):
        """Should return profile for existing user."""
        from app.models.profile import Profile

        user_id = uuid.uuid4()
        email = "admin@example.com"

        profile = Profile(id=user_id, email=email, role=UserRole.ADMIN, created_at=datetime.now(timezone.utc))
        async_session.add(profile)
        await async_session.commit()

        user_payload = {"sub": str(user_id), "email": email, "aud": JWT_AUDIENCE_AUTHENTICATED}

        result = await get_current_user_with_role(user_payload, async_session)

        assert result.id == user_id
        assert result.email == email
        assert result.role == UserRole.ADMIN

    async def test_get_user_with_role_profile_not_found(self, async_session):
        """Should auto-create profile with MEMBER role when profile not found."""
        user_id = uuid.uuid4()
        email = "newuser@example.com"
        user_payload = {"sub": str(user_id), "email": email, "aud": JWT_AUDIENCE_AUTHENTICATED}

        result = await get_current_user_with_role(user_payload, async_session)

        assert result is not None
        assert result.id == user_id
        assert result.email == email
        assert result.role == UserRole.MEMBER


class TestRequireRole:
    """Tests for require_role factory function."""

    async def test_require_admin_with_admin_user(self, async_session):
        """Should allow access for admin user requiring admin role."""
        from app.models.profile import Profile

        user_id = uuid.uuid4()
        profile = Profile(
            id=user_id, email="admin@example.com", role=UserRole.ADMIN, created_at=datetime.now(timezone.utc)
        )

        role_checker = require_role(UserRole.ADMIN)
        result = await role_checker(profile)

        assert result == profile
        assert result.role == UserRole.ADMIN

    async def test_require_admin_with_member_user(self):
        """Should raise HTTPException for member user requiring admin role."""
        from app.models.profile import Profile

        user_id = uuid.uuid4()
        profile = Profile(
            id=user_id, email="member@example.com", role=UserRole.MEMBER, created_at=datetime.now(timezone.utc)
        )

        role_checker = require_role(UserRole.ADMIN)

        with pytest.raises(HTTPException) as exc_info:
            await role_checker(profile)

        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == ERROR_INSUFFICIENT_PERMISSIONS

    async def test_require_member_with_member_user(self):
        """Should allow access for member user requiring member role."""
        from app.models.profile import Profile

        user_id = uuid.uuid4()
        profile = Profile(
            id=user_id, email="member@example.com", role=UserRole.MEMBER, created_at=datetime.now(timezone.utc)
        )

        role_checker = require_role(UserRole.MEMBER)
        result = await role_checker(profile)

        assert result == profile

    async def test_require_member_with_admin_user(self):
        """Should allow access for admin user requiring member role (hierarchical permissions)."""
        from app.models.profile import Profile

        user_id = uuid.uuid4()
        profile = Profile(
            id=user_id, email="admin@example.com", role=UserRole.ADMIN, created_at=datetime.now(timezone.utc)
        )

        role_checker = require_role(UserRole.MEMBER)
        result = await role_checker(profile)

        assert result == profile
