from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.constants import (
    APP_DESCRIPTION,
    APP_TITLE,
    APP_VERSION,
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
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://172.24.98.124:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(books.router)


@app.get("/")
async def root():
    return {"message": ROOT_MESSAGE}


@app.get("/health")
async def health():
    return {"status": HEALTH_STATUS_HEALTHY}
