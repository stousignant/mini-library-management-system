"""Tests for application models."""

import pytest

pytestmark = pytest.mark.unit


def test_user_role_enum_has_admin():
    """Test UserRole enum includes ADMIN value."""
    from app.models.enums import UserRole

    assert UserRole.ADMIN == "ADMIN"
    assert UserRole.ADMIN.value == "ADMIN"


def test_user_role_enum_has_member():
    """Test UserRole enum includes MEMBER value."""
    from app.models.enums import UserRole

    assert UserRole.MEMBER == "MEMBER"
    assert UserRole.MEMBER.value == "MEMBER"


def test_user_role_enum_all_values():
    """Test UserRole enum has exactly ADMIN and MEMBER values."""
    from app.models.enums import UserRole

    values = [role.value for role in UserRole]
    assert set(values) == {"ADMIN", "MEMBER"}
    assert len(values) == 2


def test_profile_model_structure():
    """Test Profile model has required attributes."""
    from app.models.profile import Profile

    assert hasattr(Profile, "id")
    assert hasattr(Profile, "email")
    assert hasattr(Profile, "role")
    assert hasattr(Profile, "created_at")
    assert hasattr(Profile, "__tablename__")


def test_profile_table_name():
    """Test Profile model maps to correct table name."""
    from app.models.profile import Profile

    assert Profile.__tablename__ == "profiles"
