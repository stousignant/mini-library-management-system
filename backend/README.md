# Library Management System - Backend

FastAPI backend service for the Library Management System. Provides a comprehensive REST API with authentication, role-based access control, and real-time book management capabilities.

## Features

### ✅ Minimum Requirements (Delivered)

**1. Book Management API**
- Create, read, update, delete books
- Rich metadata support (title, author, ISBN, cover images, summaries)
- Input validation and error handling

**2. Check-in/Check-out System**
- Borrow book endpoint with user tracking
- Return book endpoint with validation
- Status management (AVAILABLE/BORROWED)

**3. Search & Filtering**
- List all books endpoint
- Query by ID
- Frontend implements search by title/author

### 🚀 Extra Features (Built Beyond Minimum)

**1. Authentication & Authorization** 🔐
- Supabase JWT token validation
- Automatic user profile sync from auth.users
- Token refresh handling
- Secure password-less authentication

**2. Role-Based Access Control (RBAC)** 👥
- ADMIN and MEMBER roles
- Hierarchical permission system
- Protected endpoints with `require_role` decorator
- Flexible permission inheritance

**3. Real-time Statistics API** 📊
- Book statistics endpoint
- Aggregate counts (total, available, borrowed)
- Optimized database queries

**4. User-specific Borrowing** 📖
- Track borrower UUID on books
- User can only return own borrowed books
- Admin override capability
- Concurrency control with row-level locking

**5. Database Seeding** 🌱
- Production seeding script (100 books)
- Development quick-seed (8 books)
- Open Library API integration
- Automatic seeding on first deployment
- Idempotent and resumable

**6. Professional Development Stack** 🛠️
- Async/await throughout (AsyncSession, asyncpg)
- SQLAlchemy 2.0+ with modern mapped_column syntax
- Alembic migrations with version control
- Comprehensive test suite with pytest
- Strict linting with ruff
- Pre-commit hooks

**7. Production Ready** 🚀
- CORS with wildcard support for dynamic deployments
- Health check endpoint
- Environment-based configuration
- Docker multi-stage builds
- Database connection pooling
- Automatic migration runner

## Tech Stack

- **Framework:** FastAPI 0.115+
- **Python:** 3.11+
- **Package Manager:** uv
- **Database:** PostgreSQL with asyncpg
- **ORM:** SQLAlchemy (async)
- **Testing:** pytest with pytest-asyncio
- **Linting:** ruff

## Development Setup

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager

### Installation

```bash
# Install dependencies
uv sync --all-extras

# Copy environment variables (optional for local dev)
cp .env.example .env

# Set up pre-commit hooks (recommended)
pre-commit install

# Run tests
uv run pytest -v

# Run linting
uv run ruff check .
uv run ruff format .

# Start development server
uv run uvicorn app.main:app --reload
```

## Docker Development

```bash
# From project root
docker-compose up --build

# Backend will be available at http://localhost:8000
```

## Testing

```bash
# Run all tests
uv run pytest -v

# Run with coverage
uv run pytest --cov=app tests/
```

## Project Structure

```
backend/
├── alembic/                      # Database migrations
│   ├── versions/                 # Migration version files
│   ├── env.py                    # Alembic environment config
│   └── script.py.mako            # Migration template
├── app/
│   ├── core/
│   │   ├── config.py             # Environment configuration
│   │   ├── constants.py          # Application-wide constants (zero magic numbers)
│   │   ├── database.py           # Database session management
│   │   └── security.py           # JWT auth & role validation
│   ├── models/
│   │   ├── book.py               # Book SQLAlchemy model
│   │   ├── profile.py            # User profile model
│   │   └── enums.py              # BookStatus, UserRole enums
│   ├── routes/
│   │   ├── books.py              # Book API endpoints
│   │   └── profile.py            # Profile API endpoint
│   ├── schemas/
│   │   ├── book.py               # Pydantic schemas for books
│   │   └── profile.py            # Pydantic schemas for profiles
│   ├── services/
│   │   └── book_service.py       # Business logic for books
│   ├── __init__.py
│   └── main.py                   # FastAPI application entry point
├── scripts/
│   ├── seed_books.py             # Development seeding (8 books)
│   └── seed_production.py        # Production seeding (100 books)
├── tests/
│   ├── integration/
│   │   ├── test_books.py         # Book CRUD tests
│   │   ├── test_books_auth.py    # Auth & RBAC tests
│   │   ├── test_profile.py       # Profile endpoint tests
│   │   └── test_stats.py         # Statistics tests
│   ├── conftest.py               # Pytest fixtures (test DB, etc.)
│   ├── test_database_config.py   # Database config tests
│   ├── test_health.py            # Health check tests
│   ├── test_models.py            # Model tests
│   └── test_security.py          # Security & auth tests
├── .env.example                  # Example environment variables
├── .pre-commit-config.yaml       # Pre-commit hooks config
├── alembic.ini                   # Alembic configuration
├── Dockerfile                    # Multi-stage Docker build
├── pyproject.toml                # Project metadata and dependencies
├── start.sh                      # Production startup script
└── uv.lock                       # Locked dependencies
```

## API Endpoints

### Health
- `GET /` - Root endpoint (health check)
- `GET /health` - Detailed health status

### Books
- `POST /books/` - Create a new book
  - **Auth:** Required (ADMIN only)
  - **Body:** `{ title, author, isbn?, cover_image?, summary? }`
  - **Returns:** Created book with ID and timestamps

- `GET /books/` - List all books
  - **Auth:** None (public)
  - **Returns:** Array of all books

- `GET /books/{id}` - Get a specific book
  - **Auth:** None (public)
  - **Returns:** Book details or 404

- `PUT /books/{id}` - Update a book
  - **Auth:** Required (ADMIN only)
  - **Body:** `{ title?, author?, isbn?, cover_image?, summary?, status? }`
  - **Returns:** Updated book or 404

- `DELETE /books/{id}` - Delete a book
  - **Auth:** Required (ADMIN only)
  - **Returns:** 204 No Content or 404

- `PATCH /books/{id}/borrow` - Borrow a book
  - **Auth:** Required (MEMBER or ADMIN)
  - **Returns:** Updated book with borrowed status
  - **Errors:** 400 if already borrowed, 404 if not found

- `PATCH /books/{id}/return` - Return a book
  - **Auth:** Required (MEMBER or ADMIN)
  - **Returns:** Updated book with available status
  - **Errors:** 400 if not borrowed or not borrower, 404 if not found
  - **Note:** Members can only return their own books, admins can return any

- `GET /books/stats` - Get book statistics
  - **Auth:** None (public)
  - **Returns:** `{ total, available, borrowed }`

### Profile
- `GET /profile` - Get current user's profile
  - **Auth:** Required (MEMBER or ADMIN)
  - **Returns:** `{ id, email, role, created_at }`

## Environment Variables

See `.env.example` for all available environment variables:

- `DATABASE_URL` - PostgreSQL connection string (default: configured in docker-compose.yml)
- `ENVIRONMENT` - Application environment (development/production)
- `PYTHONUNBUFFERED` - Python output buffering (set to 1 for Docker)
- `CORS_ORIGINS` - Comma-separated list of allowed CORS origins (supports wildcards)

### CORS Configuration

The backend supports flexible CORS configuration with wildcard patterns:

**Exact Origins (No Wildcards):**
```bash
CORS_ORIGINS=https://example.com,https://app.example.com
```

**Wildcard Patterns (For Dynamic Subdomains):**
```bash
# Allow all Vercel preview deployments
CORS_ORIGINS=https://*.vercel.app

# Mix exact and wildcard patterns
CORS_ORIGINS=https://myapp.vercel.app,https://*.vercel.app,https://example.com
```

Wildcard patterns are converted to regex internally and automatically use FastAPI's `allow_origin_regex` parameter. This is particularly useful for:
- Vercel preview deployments (different URL per deployment)
- Netlify branch previews
- Any platform that generates dynamic subdomains

## Database Seeding

The application includes professional database seeding capabilities to populate the database with 100 curated books from the Open Library API.

### Quick Start

**Development Seeding (8 books):**
```bash
cd backend
uv run python -m scripts.seed_books
```

**Production Seeding (100 books):**
```bash
cd backend
uv run python -m scripts.seed_production
```

### Features

- **Automated Seeding:** Production deployments automatically seed an empty database
- **100 Curated Books:** Organized across 5 genres (Programming, Classics, Sci-Fi, Fantasy, Business)
- **Live API Integration:** Fetches real book data from Open Library API (no auth required)
- **Rich Metadata:** Includes titles, authors, cover images, and publisher information
- **Idempotent:** Safe to run multiple times (skips duplicates by ISBN)
- **Progress Tracking:** Real-time progress indicators and detailed statistics

### Book Collection

The seed data includes 100 carefully selected books across genres:
- **Programming & Tech (20):** Clean Code, Design Patterns, Pragmatic Programmer, etc.
- **Classic Literature (25):** 1984, Great Gatsby, Pride & Prejudice, To Kill a Mockingbird, etc.
- **Science Fiction (20):** Dune, Foundation, Ender's Game, Neuromancer, etc.
- **Fantasy (10):** Lord of the Rings, Harry Potter, Name of the Wind, etc.
- **Business & Non-Fiction (25):** Atomic Habits, Sapiens, Zero to One, etc.

All ISBNs are defined in `app/core/constants.py` → `SEED_BOOK_ISBNS`

### Production Deployment

Production deployments automatically handle seeding via `start.sh`:

1. **Runs migrations** (with retry logic)
2. **Checks if database is empty**
3. **Seeds 100 books if empty** (only on first deployment)
4. **Starts the application**

**Control via Environment Variable:**
```bash
# Enable/disable automatic seeding (default: true)
ENABLE_AUTO_SEED=true
```

**Manual Seeding in Production:**
```bash
# Railway
railway run python -m scripts.seed_production

# Render
# Use web dashboard: Shell → python -m scripts.seed_production

# Fly.io
fly ssh console -C "python -m scripts.seed_production"
```

### Seeding Scripts

**`scripts/seed_books.py`** - Development seeding (8 books)
- Fast seeding for local development
- Uses first 8 books from SEED_BOOK_ISBNS
- Good for quick testing

**`scripts/seed_production.py`** - Production seeding (100 books)
- Full collection with progress tracking
- Safety prompts if database has existing books
- Detailed statistics and error reporting
- Commits every 10 books for reliability

### Example Output

```
============================================================
🌱 PRODUCTION DATABASE SEEDING
============================================================

📊 Current books in database: 0

🔍 Fetching metadata for 100 books from Open Library API...
------------------------------------------------------------
[1/100] ✅ Added: Clean Code by Robert C. Martin
[2/100] ✅ Added: The Pragmatic Programmer by Andy Hunt
...
[10/100] ✅ Added: Learning Python by Mark Lutz

💾 Progress saved (committed 10 books)
...

============================================================
✨ SEEDING COMPLETE!
============================================================
📚 Created:  95 book(s)
⏭️  Skipped:  3 book(s)
⚠️  Failed:   2 book(s)
📊 Total:    95 book(s) now in database
============================================================
```

### Troubleshooting

**Seeding fails with "No module named scripts":**
- Ensure you're running from the `backend/` directory
- Use `python -m scripts.seed_production` (not `python scripts/seed_production.py`)

**Books missing cover images:**
- Some books may not have covers in Open Library
- The script continues and adds books without covers
- Frontend displays a placeholder for missing covers

**API timeout errors:**
- Open Library API is occasionally slow
- Script has 10-second timeout per book
- Failed books are logged and skipped

## Code Standards

### Constants
All magic numbers and strings must be defined in `app/core/constants.py`. This enforces:
- Single source of truth for all static values
- Easy configuration management
- Prevention of hardcoded values throughout the codebase

**Example:**
```python
# ❌ Bad - magic string
return {"status": "healthy"}

# ✅ Good - using constant
from app.core.constants import HEALTH_STATUS_HEALTHY
return {"status": HEALTH_STATUS_HEALTHY}
```
