# Library Management System

[![CI](https://github.com/stousignant/mini-library-management-system/actions/workflows/ci.yml/badge.svg)](https://github.com/stousignant/mini-library-management-system/actions/workflows/ci.yml)

A modern, full-stack library management system built with FastAPI and Vue 3, following Test-Driven Development (TDD) principles.

## Overview

This project implements a comprehensive library management system that goes beyond basic CRUD operations. It features user authentication, role-based access control, real-time statistics, advanced filtering, and a modern responsive UI—all built using TDD principles.

## Features

### ✅ Minimum Requirements (Delivered)

**1. Book Management**
- ✅ Add books (title, author, ISBN, cover image, summary)
- ✅ Edit books (update any field)
- ✅ Delete books (admin only)
- ✅ View all books in a responsive grid layout

**2. Check-in/Check-out System**
- ✅ Borrow books (mark as checked in)
- ✅ Return books (mark as checked out/available)
- ✅ Real-time status updates (AVAILABLE/BORROWED)

**3. Search Functionality**
- ✅ Search books by title
- ✅ Search books by author
- ✅ Live search with instant results

### 🚀 Extra Features (Built Beyond Minimum)

**1. Authentication & Authorization** 🔐
- Supabase-powered JWT authentication
- User profiles with email and roles
- Protected API endpoints
- Secure token validation and refresh

**2. Role-Based Access Control (RBAC)** 👥
- **ADMIN Role:**
  - Full CRUD operations on books
  - Can return any borrowed book
  - Access to administrative actions
- **MEMBER Role:**
  - Browse and search books
  - Borrow and return own books
  - View personal borrowed books
- Hierarchical permission system with inheritance

**3. Rich Book Metadata** 📚
- ISBN field support
- Cover image URLs
- Book summaries
- Creation timestamps

**4. Real-time Statistics Dashboard** 📊
- Total books count
- Available books count
- Borrowed books count
- Auto-polling updates (refreshes every 5 seconds)
- Beautiful card-based UI with icons

**5. Advanced Filtering & Sorting** 🔍
- **Filters:**
  - "My Books" - view only user's borrowed books with count badge
  - "Available Only" - show only books available to borrow
- **Sorting:**
  - Default order (by ID)
  - Alphabetical by title (A-Z)
  - By date added (newest first)

**6. User-specific Borrowing System** 📖
- Track which user borrowed which book
- Users can only return books they borrowed
- Admins can return any book
- Display borrower information

**7. Optimistic UI Updates** ⚡
- Immediate visual feedback
- Automatic rollback on errors
- Toast notifications for all actions
- Smooth state transitions

**8. Database Seeding System** 🌱
- Automated production seeding (100 curated books)
- Development quick-seed (8 books)
- Open Library API integration for real book data
- Organized across 5 genres (Programming, Classics, Sci-Fi, Fantasy, Business)
- Idempotent seeding (safe to run multiple times)
- Progress tracking and detailed statistics

**9. Professional Development Stack** 🛠️
- **Test-Driven Development (TDD):**
  - Comprehensive test suite (pytest + vitest)
  - Integration and unit tests
  - Test coverage tracking
- **Code Quality:**
  - Pre-commit hooks (ruff linting)
  - Strict type checking (mypy, TypeScript)
  - Zero magic numbers policy
- **CI/CD Pipeline:**
  - GitHub Actions for automated testing
  - Continuous deployment to Railway
  - Automatic database migrations

**10. Concurrency Control** 🔒
- Database row locking for borrow/return operations
- Prevents race conditions in multi-user scenarios
- Transaction safety

**11. Modern UI/UX** 🎨
- Beautiful card-based book display with cover images
- Dark mode support
- Fully responsive design (mobile, tablet, desktop)
- Toast notifications for user feedback
- Loading states and error handling
- Empty states with helpful messages
- Lucide icons throughout

### Data Models

**Book:**
```python
id: int
title: str
author: str
isbn: str | None
cover_image: str | None
summary: str | None
status: BookStatus  # AVAILABLE | BORROWED
borrowed_by: UUID | None  # References Profile.id
created_at: datetime
```

**Profile:**
```python
id: UUID  # Synced from Supabase auth.users
email: str
role: UserRole  # ADMIN | MEMBER
created_at: datetime
```

### API Endpoints

**Books:**
- `POST /books/` - Create a new book (admin only)
- `GET /books/` - List all books
- `GET /books/{id}` - Get a specific book
- `PUT /books/{id}` - Update a book (admin only)
- `DELETE /books/{id}` - Delete a book (admin only)
- `PATCH /books/{id}/borrow` - Borrow a book (authenticated users)
- `PATCH /books/{id}/return` - Return a book (authenticated users)
- `GET /books/stats` - Get book statistics (total, available, borrowed)

**Profile:**
- `GET /profile` - Get current user's profile (authenticated users)

## Tech Stack

### Backend
- **Framework:** FastAPI 0.115+ (Python 3.11+)
  - Modern async Python web framework
  - Automatic OpenAPI/Swagger documentation
  - High performance with async/await
- **Package Manager:** uv
  - 10-100x faster than pip
  - Cargo-inspired Python package management
  - Lock file for reproducible builds
- **Database:** PostgreSQL 15+ with asyncpg
  - Powerful relational database
  - Async driver for non-blocking queries
  - JSON support for flexible data
- **ORM:** SQLAlchemy 2.0+ (async)
  - Modern `mapped_column` syntax
  - Type-safe database operations
  - Automatic migrations with Alembic
- **Authentication:** Supabase Auth + JWT
  - Secure JWT token validation
  - Row-level security
  - Social auth support ready
- **Testing:** pytest + pytest-asyncio
  - Comprehensive test coverage
  - Async test support
  - Fixtures for test database
- **Linting:** ruff
  - Extremely fast Python linter
  - Replaces flake8, isort, pyupgrade
  - Auto-fix capabilities

### Frontend
- **Framework:** Vue 3 (Composition API, TypeScript)
  - Modern reactive UI framework
  - Composition API for better code organization
  - Full TypeScript support
- **Build Tool:** Vite
  - Lightning-fast HMR (Hot Module Replacement)
  - Optimized production builds
  - Native ES modules
- **Styling:** Tailwind CSS 3
  - Utility-first CSS framework
  - Dark mode support
  - Responsive design system
- **UI Components:** shadcn/ui (Radix Vue)
  - Accessible components
  - Customizable and unstyled
  - Beautiful default styling
- **State Management:** Pinia
  - Official Vue state management
  - TypeScript-first design
  - Devtools integration
- **HTTP Client:** Axios
  - Promise-based HTTP client
  - Request/response interceptors
  - Automatic JWT token injection
- **Testing:** vitest + vue-test-utils
  - Vite-powered test runner
  - Vue component testing utilities
  - Fast and modern

### Infrastructure
- **Containerization:** Docker & Docker Compose
  - Consistent dev/prod environments
  - Multi-stage builds for optimization
  - PostgreSQL container for local dev
- **CI/CD:** GitHub Actions → Railway
  - Automated testing on every push
  - Continuous deployment to production
  - Zero-downtime deployments
- **Database Hosting:** Supabase
  - Managed PostgreSQL
  - Built-in authentication
  - Real-time subscriptions ready
  - Generous free tier

### Development Tools
- **Version Control:** Git with pre-commit hooks
- **Code Quality:** ruff (Python), ESLint (JavaScript/TypeScript)
- **Formatting:** ruff (Python), Prettier (JavaScript/TypeScript)
- **API Documentation:** Swagger UI (auto-generated from FastAPI)
- **Database Migrations:** Alembic
- **Environment Management:** .env files with validation

## Quick Start

### Prerequisites

- [uv](https://docs.astral.sh/uv/) - Python package manager
- [Docker](https://www.docker.com/) & Docker Compose
- [Node.js](https://nodejs.org/) 18+ (for frontend)
- [pre-commit](https://pre-commit.com/) - Git hooks for code quality (optional but recommended)
- [Supabase Account](https://supabase.com/) - For authentication (free tier available)

### Local Development with Docker

```bash
# Start all services (backend + frontend + PostgreSQL)
docker-compose up --build

# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

**Docker Networking Note:** The frontend runs in the browser (not in the container), so it connects to the backend via `localhost:8000` which is exposed through Docker port mapping. The internal Docker hostname `backend` is only used for container-to-container communication.

## Authentication Setup

This application uses Supabase for authentication. You'll need to set up a Supabase project and configure the necessary credentials.

### Supabase Configuration

1. **Create a Supabase Project:**
   - Sign up at [supabase.com](https://supabase.com/)
   - Create a new project
   - Note your project URL and anon key

2. **Set Up User Roles:**
   - Navigate to SQL Editor in your Supabase dashboard
   - Run the migrations from `backend/alembic/versions/` to create the profiles table
   - The profiles table automatically syncs with auth.users via trigger
   - By default, new users get the MEMBER role

3. **Configure Environment Variables:**

**Backend (.env):**
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_JWT_SECRET=your-jwt-secret
DATABASE_URL=your-supabase-postgres-connection-string
```

**Frontend (.env.development, .env.production):**
```bash
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

4. **Create Your First Admin:**
   - Sign up through the frontend
   - In Supabase dashboard, go to Table Editor → profiles
   - Find your user and change role from 'MEMBER' to 'ADMIN'

### Authentication Flow

1. Users sign up/sign in via Supabase Auth (email + password or social providers)
2. Supabase issues a JWT token
3. Frontend stores token and includes it in API requests
4. Backend validates JWT and extracts user ID and role
5. Protected endpoints check user roles before allowing operations

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

The frontend is a modern Vue 3 application with TypeScript, Tailwind CSS, and shadcn/ui components.

```bash
cd frontend

# Install dependencies
npm install

# Run tests
npm run test

# Run tests in watch mode
npm run test:watch

# Start development server
npm run dev

# Frontend: http://localhost:5173

# Build for production
npm run build

# Preview production build
npm run preview
```

**Environment Configuration:**
- `.env.development` - Used during `npm run dev` (points to `http://localhost:8000`)
- `.env.test` - Used during testing (points to `http://localhost:8000`)
- `.env.production` - Used during `npm run build` (default: `http://localhost:8000`, update for actual production domain)

**Frontend Features:**
- 🎨 **Modern UI:** Card-based book display with cover images
- 🌙 **Dark Mode:** System-preference aware theme switching
- 📱 **Responsive:** Mobile-first design, adapts to all screen sizes
- 🔍 **Live Search:** Instant search results as you type
- 🎯 **Smart Filters:** "My Books" and "Available Only" filters
- 🔢 **Flexible Sorting:** Sort by default, title, or date added
- ⚡ **Optimistic Updates:** Immediate UI feedback with rollback
- 🔔 **Toast Notifications:** User-friendly success/error messages
- 🔄 **Auto-refresh:** Real-time polling for multi-user scenarios
- ♿ **Accessible:** Semantic HTML and ARIA labels

## Project Structure

```
.
├── .github/
│   └── workflows/
│       └── ci.yml                    # GitHub Actions CI/CD pipeline
├── backend/
│   ├── alembic/                      # Database migrations
│   ├── app/
│   │   ├── core/                     # Core configuration & security
│   │   ├── models/                   # SQLAlchemy models (Book, Profile)
│   │   ├── routes/                   # API endpoints (books, profile)
│   │   ├── schemas/                  # Pydantic request/response schemas
│   │   ├── services/                 # Business logic layer
│   │   └── main.py                   # FastAPI application
│   ├── scripts/                      # Database seeding scripts
│   ├── tests/                        # Comprehensive test suite
│   │   ├── integration/              # Integration tests for API
│   │   ├── conftest.py               # Test fixtures
│   │   └── test_*.py                 # Unit tests
│   ├── Dockerfile                    # Multi-stage uv-based build
│   ├── pyproject.toml                # Dependencies & config
│   ├── start.sh                      # Production startup script
│   └── README.md                     # Backend-specific documentation
├── frontend/
│   ├── src/
│   │   ├── components/               # Vue components
│   │   │   ├── ui/                   # Reusable UI components (shadcn/ui)
│   │   │   ├── AuthButton.vue        # Authentication UI
│   │   │   ├── BookCard.vue          # Book display card
│   │   │   ├── BookFormModal.vue     # Add/Edit book modal
│   │   │   └── BookList.vue          # Main book list view
│   │   ├── composables/              # Vue composables (useTheme)
│   │   ├── services/                 # API client & Supabase config
│   │   ├── stores/                   # Pinia state management
│   │   │   ├── authStore.ts          # Authentication state
│   │   │   ├── bookStore.ts          # Book state & operations
│   │   │   └── statsStore.ts         # Statistics state
│   │   ├── types/                    # TypeScript type definitions
│   │   └── App.vue                   # Root component
│   ├── Dockerfile                    # Frontend production build
│   ├── package.json                  # Frontend dependencies
│   └── vite.config.ts                # Vite configuration
├── docker-compose.yml                # Local dev orchestration
└── README.md                         # Main project documentation
```

## Development Workflow

### Test-Driven Development (TDD)

This project follows strict TDD principles for all feature development:

1. **🔴 RED:** Write a failing test first
   - Define the expected behavior
   - Run the test to confirm it fails
   - Understand what needs to be implemented

2. **🟢 GREEN:** Write minimum code to pass
   - Implement just enough code to make the test pass
   - Don't worry about perfection yet
   - Focus on functionality

3. **🔵 REFACTOR:** Clean and optimize
   - Improve code quality
   - Remove duplication
   - Optimize performance
   - Ensure tests still pass

4. **💾 COMMIT:** Atomic commits per feature
   - One logical change per commit
   - Follow Conventional Commits format
   - Write meaningful commit messages

### Code Quality Standards

**Zero Magic Numbers:** All constants must be defined in `constants.py` or environment variables

**Self-Documenting Code:** Code must be readable without comments

**Linting & Formatting:**
```bash
# Backend
cd backend
uv run ruff check .        # Lint
uv run ruff format .        # Format

# Frontend
cd frontend
npm run lint               # ESLint
npm run format             # Prettier
```

**Pre-commit Hooks:** Automatically run linting and formatting before each commit

## CI/CD Pipeline

### Continuous Integration (GitHub Actions)

**Triggers:** Push to `main`, Pull Requests

**Backend Pipeline:**
- ✅ Python 3.11 environment setup
- ✅ Install uv package manager
- ✅ Install dependencies
- ✅ Linting with ruff (`ruff check`)
- ✅ Format checking with ruff (`ruff format --check`)
- ✅ Full test suite with pytest
- ✅ PostgreSQL service container for integration tests

**Frontend Pipeline:**
- ✅ Node.js 18 environment setup
- ✅ Install dependencies
- ✅ Run vitest test suite
- ✅ Component and store tests

**Quality Gates:**
- All tests must pass
- No linting errors
- Code must be properly formatted

### Continuous Deployment (Railway)

**Trigger:** Successful CI build on `main` branch

**Deployment Process:**
1. Docker multi-stage build (backend + frontend)
2. Run Alembic migrations automatically
3. Seed database if empty (100 books from Open Library)
4. Start FastAPI server with uvicorn
5. Serve frontend static files

**Infrastructure:**
- Backend: Railway (FastAPI + uvicorn)
- Database: Supabase (PostgreSQL)
- Frontend: Served as static files from backend

**Environment Variables Required:**
- `DATABASE_URL` - Supabase PostgreSQL connection string
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_JWT_SECRET` - JWT secret for token validation
- `CORS_ORIGINS` - Allowed CORS origins
- `ENABLE_AUTO_SEED` - Enable automatic database seeding (default: true)

## Testing

This project follows Test-Driven Development (TDD) principles with comprehensive test coverage.

### Backend Testing (pytest)

```bash
cd backend

# Run all tests
uv run pytest -v

# Run specific test file
uv run pytest tests/integration/test_books.py -v

# Run specific test function
uv run pytest tests/integration/test_books.py::test_create_book -v

# Run with coverage report
uv run pytest --cov=app --cov-report=term-missing

# Run tests matching a pattern
uv run pytest -k "borrow" -v
```

**Test Coverage:**
- ✅ Health check endpoints
- ✅ Database configuration and connections
- ✅ Book CRUD operations (create, read, update, delete)
- ✅ Borrow/return workflows
- ✅ Authentication & JWT validation
- ✅ Role-based access control (ADMIN vs MEMBER)
- ✅ Book statistics calculations
- ✅ Profile endpoints
- ✅ Model validations
- ✅ Security utilities

### Frontend Testing (vitest)

```bash
cd frontend

# Run all tests
npm run test

# Run tests in watch mode
npm run test:watch

# Run with coverage
npm run test:coverage
```

**Test Coverage:**
- ✅ Book list component rendering
- ✅ Book store state management
- ✅ Stats store state management
- ✅ Auth store state management
- ✅ Component interactions

### Test Database

Tests use a Dockerized PostgreSQL database (configured in `conftest.py`) to ensure tests match the production environment. The test database is automatically set up and torn down for each test session.

## License

See [LICENSE](LICENSE) file for details.
