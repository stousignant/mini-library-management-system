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
BOOK_COVER_IMAGE_MAX_LENGTH = 500
BOOK_SUMMARY_MAX_LENGTH = 1000
BOOK_FIELD_MIN_LENGTH = 1

# Database Configuration
DB_TEST_CONNECT_ARGS = {"server_settings": {"jit": "off"}, "ssl": "disable"}
DEFAULT_TEST_DB_URL = "postgresql+asyncpg://postgres:postgres@localhost:5433/library_test"

# CORS Configuration
DEFAULT_CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_METHODS = ["*"]
CORS_ALLOW_ALL_HEADERS = ["*"]

# Open Library API Configuration
OPEN_LIBRARY_API_BASE_URL = "https://openlibrary.org"
OPEN_LIBRARY_COVERS_BASE_URL = "https://covers.openlibrary.org"

# Seed Data Configuration
SEED_BOOK_ISBNS = [
    "9780451524935",
    "9780743273565",
    "9780345391803",
    "9780061120084",
    "9780547928227",
    "9780441013593",
    "9780321125217",
    "9780131103627",
]
