# Library Management System

[![CI](https://github.com/stousignant/mini-library-management-system/actions/workflows/ci.yml/badge.svg)](https://github.com/stousignant/mini-library-management-system/actions/workflows/ci.yml)

A modern, full-stack library management system built with FastAPI and Vue 3, following Test-Driven Development (TDD) principles.

## Overview

This project is a strict MVP implementation focusing on core CRUD operations and business logic for managing books, users, and borrow logs.

## Tech Stack

### Backend
- **Framework:** FastAPI (Python 3.11+)
- **Package Manager:** uv (modern Python package manager)
- **Database:** PostgreSQL with asyncpg
- **ORM:** SQLAlchemy (async)
- **Testing:** pytest + pytest-asyncio
- **Linting:** ruff

### Frontend
- **Framework:** Vue 3 (Composition API, TypeScript)
- **Styling:** Tailwind CSS
- **State Management:** Pinia
- **Testing:** vitest + vue-test-utils

### Infrastructure
- **Containerization:** Docker & Docker Compose
- **CI/CD:** GitHub Actions → Railway
- **Database Hosting:** Supabase

## Quick Start

### Prerequisites

- [uv](https://docs.astral.sh/uv/) - Python package manager
- [Docker](https://www.docker.com/) & Docker Compose
- [Node.js](https://nodejs.org/) 18+ (for frontend)
- [pre-commit](https://pre-commit.com/) - Git hooks for code quality (optional but recommended)

### Local Development with Docker

```bash
# Start all services (backend + frontend + PostgreSQL)
docker-compose up --build

# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

**Docker Networking Note:** The frontend runs in the browser (not in the container), so it connects to the backend via `localhost:8000` which is exposed through Docker port mapping. The internal Docker hostname `backend` is only used for container-to-container communication.

### Backend Development

```bash
cd backend

# Install dependencies
uv sync --all-extras

# Set up pre-commit hooks (recommended)
pre-commit install

# Run tests
uv run pytest -v

# Run linting
uv run ruff check .

# Start development server
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run tests
npm run test

# Start development server
npm run dev

# Frontend: http://localhost:5173
```

**Environment Configuration:**
- `.env.development` - Used during `npm run dev` (points to `http://localhost:8000`)
- `.env.test` - Used during testing (points to `http://localhost:8000`)
- `.env.production` - Used during `npm run build` (default: `http://localhost:8000`, update for actual production domain)

## Project Structure

```
.
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI pipeline
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py             # FastAPI application
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_health.py      # Health check tests
│   ├── Dockerfile              # Multi-stage uv-based build
│   ├── pyproject.toml          # Dependencies & config
│   └── uv.lock                 # Locked dependencies
├── docker-compose.yml          # Local dev orchestration
└── README.md
```

## Development Workflow

This project follows strict TDD principles:

1. **🔴 RED:** Write a failing test first
2. **🟢 GREEN:** Write minimum code to pass
3. **🔵 REFACTOR:** Clean and optimize
4. **💾 COMMIT:** Atomic commits per feature

## CI/CD Pipeline

### Continuous Integration (GitHub Actions)
- **Triggers:** Push to `main`, Pull Requests
- **Jobs:**
  - Backend linting (ruff)
  - Backend tests (pytest)
  - Frontend tests (vitest) - *coming soon*

### Continuous Deployment (Railway)
- **Trigger:** Successful build on `main`
- **Action:** Docker build → Deploy

## Core Features (MVP)

### Data Models
- **Book:** `id`, `title`, `author`, `isbn`, `status`, `created_at`
- **User:** `id`, `email`, `role`
- **BorrowLog:** `id`, `book_id`, `user_id`, `borrowed_at`, `returned_at`

### API Endpoints
*Coming soon as we implement with TDD*

## Testing

```bash
# Backend tests
cd backend
uv run pytest -v

# Frontend tests (coming soon)
cd frontend
npm run test
```

## License

See [LICENSE](LICENSE) file for details.
