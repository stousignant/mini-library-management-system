"""
Authentication and authorization utilities.

Handles JWT token verification, user authentication, and role-based access control.
"""

import logging
import time
from uuid import UUID

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwk, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.constants import (
    ERROR_INSUFFICIENT_PERMISSIONS,
    ERROR_INVALID_TOKEN,
    JWKS_CACHE_TTL_SECONDS,
    JWT_AUDIENCE_AUTHENTICATED,
    SUPABASE_JWKS_PATH,
)
from app.core.database import get_db
from app.models.enums import UserRole
from app.models.profile import Profile

logger = logging.getLogger(__name__)

oauth2_scheme = HTTPBearer()

_jwks_cache = {"data": None, "timestamp": 0}


def get_supabase_jwks_url() -> str:
    """Get Supabase JWKS URL from settings."""
    settings = get_settings()
    if not settings.supabase_url:
        raise ValueError("SUPABASE_URL must be set in environment variables")
    return f"{settings.supabase_url.rstrip('/')}{SUPABASE_JWKS_PATH}"


def get_supabase_jwks() -> dict:
    """
    Fetch JWKS (JSON Web Key Set) from Supabase with time-based cache.

    Cache expires after JWKS_CACHE_TTL_SECONDS (default 1 hour) to handle
    key rotation. If network fails but cached data exists, uses stale cache
    as fallback.

    Returns:
        Dictionary of JWKS containing public keys

    Raises:
        HTTPException: 500 if unable to fetch JWKS and no cached data available
    """
    current_time = time.time()

    if _jwks_cache["data"] is not None and current_time - _jwks_cache["timestamp"] < JWKS_CACHE_TTL_SECONDS:
        return _jwks_cache["data"]

    jwks_url = get_supabase_jwks_url()
    try:
        response = httpx.get(jwks_url, timeout=5.0)
        response.raise_for_status()
        jwks = response.json()

        _jwks_cache["data"] = jwks
        _jwks_cache["timestamp"] = current_time

        return jwks
    except Exception as e:
        if _jwks_cache["data"] is not None:
            logger.warning(f"JWKS fetch failed, using cached data: {e}")
            return _jwks_cache["data"]

        logger.error(f"Failed to fetch JWKS from {jwks_url}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch authentication keys"
        )


def get_signing_key(token: str) -> str:
    """
    Get the public key for verifying JWT token signature.

    Args:
        token: JWT token string

    Returns:
        Public key constructed from JWK

    Raises:
        HTTPException: 401 if unable to find matching key
    """
    try:
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")

        if not kid:
            logger.error("Token missing key ID (kid)")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing key ID")

        jwks = get_supabase_jwks()

        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                return jwk.construct(key)

        logger.error(f"No matching key found for kid: {kid}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unable to find matching signing key")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting signing key: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ERROR_INVALID_TOKEN)


def decode_jwt_token(token: str) -> dict:
    """
    Decode and validate JWT token with ES256 or HS256 algorithm.

    In test environment: Uses HS256 with JWT secret for test tokens.
    In production: Strictly uses ES256 with public keys from JWKS endpoint.

    Args:
        token: JWT token string

    Returns:
        Decoded token payload

    Raises:
        HTTPException: 401 if token is invalid, expired, or signature verification fails
    """
    settings = get_settings()
    if settings.environment == "test":
        try:
            payload = jwt.decode(
                token,
                settings.supabase_jwt_secret,
                algorithms=["HS256"],
                audience=JWT_AUDIENCE_AUTHENTICATED,
                options={"verify_aud": True},
            )
            logger.info(f"JWT verified (HS256/test) for user: {payload.get('email')}")
            return payload
        except JWTError as e:
            logger.error(f"JWT verification failed: {type(e).__name__}: {str(e)}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ERROR_INVALID_TOKEN)

    try:
        public_key = get_signing_key(token)

        payload = jwt.decode(
            token,
            public_key,
            algorithms=["ES256"],
            audience=JWT_AUDIENCE_AUTHENTICATED,
            options={"verify_aud": True},
        )
        logger.info(f"JWT verified (ES256) for user: {payload.get('email')}")
        return payload
    except HTTPException:
        raise
    except JWTError as e:
        logger.error(f"JWT verification failed: {type(e).__name__}: {str(e)}")
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

    If profile doesn't exist, creates it automatically with MEMBER role.

    Args:
        user: User payload from JWT token
        db: Database session

    Returns:
        User profile with role information
    """
    user_id = UUID(user["sub"])
    email = user.get("email")

    result = await db.execute(select(Profile).where(Profile.id == user_id))
    profile = result.scalar_one_or_none()

    if profile is None:
        profile = Profile(id=user_id, email=email, role=UserRole.MEMBER)
        db.add(profile)
        await db.commit()
        await db.refresh(profile)

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
