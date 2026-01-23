"""
Authentication and authorization utilities.

Handles JWT token verification, user authentication, and role-based access control.
"""

from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.constants import (
    ERROR_INSUFFICIENT_PERMISSIONS,
    ERROR_INVALID_TOKEN,
    ERROR_USER_NOT_FOUND,
    JWT_ALGORITHM,
    JWT_AUDIENCE_AUTHENTICATED,
)
from app.core.database import get_db
from app.models.enums import UserRole
from app.models.profile import Profile

settings = get_settings()

oauth2_scheme = HTTPBearer()


def decode_jwt_token(token: str) -> dict:
    """
    Decode and validate JWT token from Supabase.

    Args:
        token: JWT token string

    Returns:
        Decoded token payload

    Raises:
        HTTPException: 401 if token is invalid, expired, or has wrong audience
    """
    try:
        payload = jwt.decode(
            token, settings.supabase_jwt_secret, algorithms=[JWT_ALGORITHM], audience=JWT_AUDIENCE_AUTHENTICATED
        )
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ERROR_INVALID_TOKEN)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)) -> dict:
    """
    Extract and validate current user from JWT token.

    Args:
        credentials: HTTP Bearer token credentials

    Returns:
        User payload from decoded token

    Raises:
        HTTPException: 401 if token is invalid
    """
    token = credentials.credentials
    return decode_jwt_token(token)


async def get_current_user_with_role(
    user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> Profile:
    """
    Fetch user profile with role from database.

    Args:
        user: User payload from JWT token
        db: Database session

    Returns:
        User profile with role information

    Raises:
        HTTPException: 404 if profile not found
    """
    user_id = UUID(user["sub"])

    result = await db.execute(select(Profile).where(Profile.id == user_id))
    profile = result.scalar_one_or_none()

    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_USER_NOT_FOUND)

    return profile


def require_role(required_role: UserRole):
    """
    Factory function to create role-checking dependency.

    Args:
        required_role: Role required to access the endpoint

    Returns:
        Dependency function that checks user role

    Raises:
        HTTPException: 403 if user lacks required role
    """

    async def role_checker(profile: Profile = Depends(get_current_user_with_role)) -> Profile:
        if profile.role != required_role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_INSUFFICIENT_PERMISSIONS)
        return profile

    return role_checker
