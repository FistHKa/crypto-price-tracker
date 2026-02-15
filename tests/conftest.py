import os
from datetime import datetime, timezone
from typing import AsyncIterator, Iterator

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.pool import NullPool

from app.main import app


@pytest.fixture(scope="session")
def database_url() -> str:
    """Async DATABASE_URL from env (docker-compose.test.yml sets it)."""
    url = os.environ["DATABASE_URL"]

    if "test" not in url.lower():
        raise RuntimeError(f"Refusing to run tests on non-test DB: {url}")
    return url


@pytest.fixture(scope="session")
def sync_database_url(database_url: str) -> str:
    """Convert async DB URL to sync URL for maintenance SQL (TRUNCATE)."""
    # postgresql+asyncpg -> postgresql+psycopg
    return database_url.replace("+asyncpg", "+psycopg")


@pytest.fixture
async def engine(database_url: str) -> AsyncIterator[AsyncEngine]:
    """
    Async engine per test (function scope) to avoid loop issues.
    Always disposed at the end of the test.
    """
    eng = create_async_engine(database_url, echo=False, poolclass=NullPool)
    try:
        print("TEST ENGINE", id(eng))
        yield eng
    finally:
        await eng.dispose()


@pytest.fixture(scope="session")
def sync_engine(sync_database_url: str) -> Engine:
    """
    Sync engine used only for TRUNCATE/maintenance.
    Avoids asyncpg 'operation in progress' and loop issues.
    """
    return create_engine(sync_database_url, future=True, poolclass=NullPool)


@pytest.fixture(autouse=True)
def clean_db(sync_engine: Engine) -> Iterator[None]:
    """
    Clean DB before EACH test, so tests are deterministic and independent.
    """
    with sync_engine.begin() as conn:
        conn.exec_driver_sql("TRUNCATE TABLE prices RESTART IDENTITY CASCADE;")
    yield


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    """
    Async HTTP client for FastAPI app without running a real server.
    """
    transport = ASGITransport(app=app)
    async with LifespanManager(app):
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac


@pytest.fixture
async def seed_prices(engine: AsyncEngine) -> AsyncIterator[dict]:
    """
    Inserts deterministic rows into TEST DB with explicit timestamps.
    Returns dict with timestamps for test assertions.
    """
    t1 = datetime(2026, 2, 3, 20, 45, 0, tzinfo=timezone.utc)
    t2 = datetime(2026, 2, 3, 20, 46, 0, tzinfo=timezone.utc)
    t3 = datetime(2026, 2, 3, 20, 47, 0, tzinfo=timezone.utc)

    async with engine.begin() as conn:
        await conn.execute(
            text(
                "INSERT INTO prices (ticker, price, timestamp) VALUES ('BTC', 100.12, :ts)"),
            {"ts": t1},
        )
        await conn.execute(
            text(
                "INSERT INTO prices (ticker, price, timestamp) VALUES ('BTC', 101.34, :ts)"),
            {"ts": t3},
        )
        await conn.execute(
            text(
                "INSERT INTO prices (ticker, price, timestamp) VALUES ('ETH', 200.50, :ts)"),
            {"ts": t2},
        )

    yield {"t1": t1, "t2": t2, "t3": t3}
