"""
Profile API endpoints.

Provides endpoints for retrieving user profile information.
"""

from fastapi import APIRouter, Depends

from app.core.security import get_current_user_with_role
from app.models.profile import Profile
from app.schemas.profile import ProfileResponse

router = APIRouter()


@router.get("/profile", response_model=ProfileResponse)
async def get_current_user_profile(current_user: Profile = Depends(get_current_user_with_role)):
    """
    Get current user's profile.

    Returns the authenticated user's profile including their role.
    """
    return current_user
