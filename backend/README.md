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
│   ├── __init__.py
│   └── main.py           # FastAPI application entry point
├── tests/
│   ├── __init__.py
│   └── test_health.py    # Health check tests
├── Dockerfile            # Multi-stage Docker build
├── pyproject.toml        # Project metadata and dependencies
└── uv.lock              # Locked dependencies
```

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check endpoint

## Environment Variables

- `DATABASE_URL` - PostgreSQL connection string (default: configured in docker-compose.yml)
