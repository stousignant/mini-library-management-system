"""
Enums for application models.

Defines all enumerated types used across the application to ensure
type safety and consistency.
"""

from enum import Enum


class BookStatus(str, Enum):
    """Status of a book in the library system."""

    AVAILABLE = "AVAILABLE"
    BORROWED = "BORROWED"


class UserRole(str, Enum):
    """Role of a user in the system with hierarchical permissions."""

    ADMIN = "ADMIN"
    MEMBER = "MEMBER"

    def has_permission(self, required_role: "UserRole") -> bool:
        """
        Check if this role has permission of required role.

        Uses role hierarchy where higher roles include lower role permissions.

        Args:
            required_role: The role permission being checked

        Returns:
            True if this role has the required permission level
        """
        role_hierarchy = {
            UserRole.ADMIN: 2,
            UserRole.MEMBER: 1,
        }
        return role_hierarchy.get(self, 0) >= role_hierarchy.get(required_role, 0)
