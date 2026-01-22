from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_cors_origins
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
from app.routes import books

app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=CORS_ALLOW_ALL_METHODS,
    allow_headers=CORS_ALLOW_ALL_HEADERS,
)

app.include_router(books.router)


@app.get("/")
async def root():
    return {"message": ROOT_MESSAGE}


@app.get("/health")
async def health():
    return {"status": HEALTH_STATUS_HEALTHY}
