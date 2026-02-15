from datetime import datetime, timedelta

import pytest
from httpx import AsyncClient

from app.core.config import settings


# ===== Timestamp helpers =====

def api_ts_to_dt(ts: str) -> datetime:
    """Convert API ISO timestamp (Z) to timezone-aware datetime."""
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def dt_to_api_ts(dt: datetime) -> str:
    """Convert datetime to API ISO timestamp with Z suffix."""
    return dt.isoformat().replace("+00:00", "Z")


# ===== Tests =====

async def test_health_ok(client: AsyncClient) -> None:
    """GET /health must return service status."""
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "app_name": settings.app_name,
        "env": settings.env,
    }


async def test_prices_latest_returns_single_row(client: AsyncClient, seed_prices: dict) -> None:
    """
    GET /prices/latest?ticker=BTC must return the most recent BTC row.
    """
    response = await client.get("/prices/latest", params={"ticker": "BTC"})
    assert response.status_code == 200

    data = response.json()
    assert data["ticker"] == "BTC"
    assert data["price"] == 101.34

    # timestamp should be >= latest timestamp (exact match is also ok)
    ts = api_ts_to_dt(data["timestamp"])
    assert ts == seed_prices["t3"]


async def test_prices_all_returns_list_for_ticker(client: AsyncClient, seed_prices: dict) -> None:
    """
    GET /prices?ticker=BTC must return a list of BTC rows.
    """
    response = await client.get("/prices/", params={"ticker": "BTC"})
    assert response.status_code == 200

    items = response.json()
    assert isinstance(items, list)
    assert len(items) == 2
    assert all(x["ticker"] == "BTC" for x in items)


async def test_prices_by_date_filters_range(client: AsyncClient, seed_prices: dict) -> None:
    """
    GET /prices/by-date must return only rows within [date_from, date_to] for ticker.
    """
    date_from = dt_to_api_ts(seed_prices["t1"])
    date_to = dt_to_api_ts(seed_prices["t1"] + timedelta(seconds=59))

    response = await client.get(
        "/prices/by-date",
        params={
            "ticker": "BTC",
            "date_from": date_from,
            "date_to": date_to,
            "limit": 1000,
            "offset": 0,
        },
    )
    assert response.status_code == 200

    items = response.json()
    assert isinstance(items, list)
    assert len(items) == 1
    assert items[0]["ticker"] == "BTC"
    assert items[0]["price"] == 100.12

    ts = api_ts_to_dt(items[0]["timestamp"])
    assert ts == seed_prices["t1"]
