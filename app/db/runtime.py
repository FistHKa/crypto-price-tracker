from __future__ import annotations

from typing import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings


@asynccontextmanager
async def session_scope() -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    engine = create_async_engine(settings.database_url, echo=False)
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    try:
        yield SessionLocal
    finally:
        await engine.dispose()
