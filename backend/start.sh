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
fi

echo "Starting uvicorn server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
