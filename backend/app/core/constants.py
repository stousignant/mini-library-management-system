"""
Application-wide constants and configuration values.

This module centralizes all static values, magic numbers, and configuration
to maintain a single source of truth and prevent hardcoded values throughout
the codebase.
"""

from app.models.enums import BookStatus

# Application Metadata
APP_TITLE = "Library Management System"
APP_DESCRIPTION = "MVP API for managing books, users, and borrow logs"
APP_VERSION = "0.1.0"

# API Endpoints
ROOT_MESSAGE = "Library Management System API"
HEALTH_STATUS_HEALTHY = "healthy"

# Server Configuration
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8000

# Book Configuration
DEFAULT_BOOK_STATUS = BookStatus.AVAILABLE
BOOK_TITLE_MAX_LENGTH = 255
BOOK_AUTHOR_MAX_LENGTH = 255
BOOK_ISBN_MAX_LENGTH = 20
BOOK_FIELD_MIN_LENGTH = 1

# Database Configuration
DB_TEST_CONNECT_ARGS = {"server_settings": {"jit": "off"}, "ssl": "disable"}
DEFAULT_TEST_DB_URL = "postgresql+asyncpg://postgres:postgres@localhost:5433/library_test"
