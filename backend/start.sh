#!/bin/bash
set -e

echo "Starting application..."

if [ "$ENVIRONMENT" = "production" ]; then
    echo "Running database migrations..."

    MAX_RETRIES=5
    RETRY_DELAY=3
    retry_count=0

    while [ $retry_count -lt $MAX_RETRIES ]; do
        if alembic upgrade head; then
            echo "Migrations completed successfully"
            break
        else
            retry_count=$((retry_count + 1))
            if [ $retry_count -lt $MAX_RETRIES ]; then
                echo "Migration attempt $retry_count failed. Retrying in ${RETRY_DELAY}s..."
                sleep $RETRY_DELAY
            else
                echo "Migration failed after $MAX_RETRIES attempts"
                exit 1
            fi
        fi
    done

    # Database seeding for production
    ENABLE_AUTO_SEED="${ENABLE_AUTO_SEED:-true}"

    if [ "$ENABLE_AUTO_SEED" = "true" ]; then
        echo "Checking if database needs seeding..."

        # Count existing books in the database
        BOOK_COUNT=$(python -c "
import asyncio
from app.core.database import AsyncSessionLocal
from app.models.book import Book
from sqlalchemy import select, func

async def count_books():
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(func.count(Book.id)))
            count = result.scalar()
            print(count if count is not None else 0)
    except Exception as e:
        print(0)

asyncio.run(count_books())
" 2>/dev/null || echo "0")

        echo "Current books in database: $BOOK_COUNT"

        if [ "$BOOK_COUNT" = "0" ]; then
            echo "Database is empty. Running seed script..."
            if python -m scripts.seed_books; then
                echo "Database seeded successfully"
            else
                echo "Warning: Seeding failed, but continuing with application startup"
            fi
        else
            echo "Database already contains books. Skipping seed."
        fi
    else
        echo "Auto-seeding is disabled (ENABLE_AUTO_SEED=false)"
    fi
fi

echo "Starting uvicorn server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
