# Library Management System - Backend

FastAPI backend service for the Library Management System.

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
├── app/
│   ├── core/
│   │   ├── __init__.py
│   │   └── constants.py  # Application-wide constants (zero magic numbers policy)
│   ├── __init__.py
│   └── main.py           # FastAPI application entry point
├── tests/
│   ├── __init__.py
│   └── test_health.py    # Health check tests
├── .env.example          # Example environment variables
├── Dockerfile            # Multi-stage Docker build
├── pyproject.toml        # Project metadata and dependencies
└── uv.lock              # Locked dependencies
```

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check endpoint

## Environment Variables

See `.env.example` for all available environment variables:

- `DATABASE_URL` - PostgreSQL connection string (default: configured in docker-compose.yml)
- `ENVIRONMENT` - Application environment (development/production)
- `PYTHONUNBUFFERED` - Python output buffering (set to 1 for Docker)

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
