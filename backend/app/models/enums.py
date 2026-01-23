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
    """Role of a user in the system."""

    ADMIN = "ADMIN"
    MEMBER = "MEMBER"
