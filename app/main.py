import app.core.logging

from fastapi import FastAPI

from app.core.config import settings
from app.api.prices import router as prices_router

app = FastAPI(title=settings.app_name)

app.include_router(prices_router)


@app.get('/health')
def health() -> dict:
    return {
        "status": "ok",
        "app_name": settings.app_name,
        "env": settings.env,
    }
