from __future__ import annotations

import asyncio
import logging
from decimal import Decimal

import aiohttp
from celery import shared_task

from app.clients.deribit import DeribitClient
from app.repositories.prices import create_price
from app.db.runtime import session_scope

logger = logging.getLogger(__name__)


async def _fetch_and_store() -> None:
    client = DeribitClient()
    tickers = ["BTC", "ETH"]

    async with aiohttp.ClientSession() as http:
        async with session_scope() as SessionLocal:

            async def one_ticker(ticker: str) -> None:
                price = await client.get_index_price(ticker, session=http)
                async with SessionLocal() as db:
                    await create_price(db, ticker=ticker, price=price)

            results = await asyncio.gather(
                *(one_ticker(t) for t in tickers),
                return_exceptions=True,
            )

    for t, r in zip(tickers, results):
        if isinstance(r, Exception):
            logger.exception("fetch_and_store failed for ticker=%s: %r", t, r)


@shared_task(name="app.tasks.prices.fetch_and_store_prices")
def fetch_and_store_prices() -> None:
    """
    Celery task entrypoint (sync), runs async workflow inside.
    """
    asyncio.run(_fetch_and_store())
