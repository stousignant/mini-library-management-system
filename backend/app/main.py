import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import make_url

from app.core.config import get_cors_origin_regex, get_cors_origins, get_settings
from app.core.constants import (
    APP_DESCRIPTION,
    APP_TITLE,
    APP_VERSION,
    CORS_ALLOW_ALL_HEADERS,
    CORS_ALLOW_ALL_METHODS,
    CORS_ALLOW_CREDENTIALS,
    HEALTH_STATUS_HEALTHY,
    ROOT_MESSAGE,
)
from app.routes import books, profile

logger = logging.getLogger(__name__)

settings = get_settings()
db_url = make_url(settings.database_url)

print("\n" + "=" * 80)
print("APPLICATION STARTUP - Settings Check")
print("=" * 80)
print(f"Environment: {settings.environment}")
print(f"Database host: {db_url.host}")
print(f"Database port: {db_url.port}")
print(f"Database name: {db_url.database}")
print(f"Supabase URL configured: {settings.supabase_url is not None}")
print(f"Supabase URL value: {settings.supabase_url if settings.supabase_url else 'NOT SET'}")
print("=" * 80 + "\n")

logger.info(f"Environment: {settings.environment}")
logger.info(f"Database host: {db_url.host}")
logger.info(f"Database port: {db_url.port}")
logger.info(f"Database name: {db_url.database}")
logger.info(f"Supabase URL configured: {settings.supabase_url is not None}")
logger.info(f"Supabase URL value: {settings.supabase_url if settings.supabase_url else 'NOT SET'}")

app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
)

cors_regex = get_cors_origin_regex()
if cors_regex:
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=cors_regex,
        allow_credentials=CORS_ALLOW_CREDENTIALS,
        allow_methods=CORS_ALLOW_ALL_METHODS,
        allow_headers=CORS_ALLOW_ALL_HEADERS,
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_cors_origins(),
        allow_credentials=CORS_ALLOW_CREDENTIALS,
        allow_methods=CORS_ALLOW_ALL_METHODS,
        allow_headers=CORS_ALLOW_ALL_HEADERS,
    )

app.include_router(books.router)
app.include_router(profile.router)


@app.get("/")
async def root():
    return {"message": ROOT_MESSAGE}


@app.get("/health")
async def health():
    from sqlalchemy import text

    from app.core.database import async_engine

    db_status = "unknown"
    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            db_status = "connected"
    except Exception as e:
        db_status = f"error: {type(e).__name__}"
        logger.error(f"Database health check failed: {e}")

    return {
        "status": HEALTH_STATUS_HEALTHY,
        "database": db_status,
        "environment": settings.environment,
    }
