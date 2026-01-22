#!/bin/bash
set -e

echo "Starting application..."

if [ "$ENVIRONMENT" = "production" ]; then
    echo "Running database migrations..."
    alembic upgrade head
    echo "Migrations completed successfully"
fi

echo "Starting uvicorn server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
