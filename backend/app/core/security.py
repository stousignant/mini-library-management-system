"""
Authentication and authorization utilities.

Handles JWT token verification, user authentication, and role-based access control.
"""

import logging
from functools import lru_cache
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
)
from app.core.database import get_db
from app.models.enums import UserRole
from app.models.profile import Profile

settings = get_settings()
logger = logging.getLogger(__name__)

oauth2_scheme = HTTPBearer()

SUPABASE_JWKS_URL = "https://lmchwrrswvllapfhohnb.supabase.co/auth/v1/.well-known/jwks.json"


@lru_cache(maxsize=1)
def get_supabase_jwks() -> dict:
    """
    Fetch JWKS (JSON Web Key Set) from Supabase.

    Cached to avoid repeated HTTP requests.

    Returns:
        Dictionary of JWKS containing public keys

    Raises:
        HTTPException: 500 if unable to fetch JWKS
    """
    try:
        response = httpx.get(SUPABASE_JWKS_URL, timeout=5.0)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to fetch JWKS from {SUPABASE_JWKS_URL}: {e}")
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

    For production: Fetches ES256 public key from Supabase's JWKS endpoint.
    For testing: Falls back to HS256 with JWT secret if ES256 verification fails.

    Args:
        token: JWT token string

    Returns:
        Decoded token payload

    Raises:
        HTTPException: 401 if token is invalid, expired, or signature verification fails
    """
    try:
        public_key = get_signing_key(token)

        payload = jwt.decode(
            token,
            public_key,
            algorithms=["ES256"],
            options={"verify_aud": False},
        )
        logger.info(f"JWT verified (ES256) for user: {payload.get('email')}")
        return payload
    except HTTPException as e:
        if e.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            raise
        try:
            payload = jwt.decode(
                token,
                settings.supabase_jwt_secret,
                algorithms=["HS256"],
                options={"verify_aud": False},
            )
            logger.info(f"JWT verified (HS256) for user: {payload.get('email')}")
            return payload
        except JWTError as e2:
            logger.error(f"JWT verification failed (both ES256 and HS256): {type(e2).__name__}: {str(e2)}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ERROR_INVALID_TOKEN)
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
