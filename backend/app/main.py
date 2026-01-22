from fastapi import FastAPI

from app.core.constants import (
    APP_DESCRIPTION,
    APP_TITLE,
    APP_VERSION,
    HEALTH_STATUS_HEALTHY,
    ROOT_MESSAGE,
)

app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
)


@app.get("/")
async def root():
    return {"message": ROOT_MESSAGE}


@app.get("/health")
async def health():
    return {"status": HEALTH_STATUS_HEALTHY}
