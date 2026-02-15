from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

import aiohttp


@dataclass(frozen=True)
class DeribitClient:
    base_url: str = "https://www.deribit.com/api/v2"

    async def get_index_price(self, ticker: str, session: aiohttp.ClientSession) -> Decimal:
        """
        Fetch index price for a given ticker.

        Expected tickers: "BTC", "ETH"
        Deribit index names: "btc_usd", "eth_usd"
        """
        index_name = self._to_index_name(ticker)

        url = f"{self.base_url}/public/get_index_price"
        params = {"index_name": index_name}

        async with session.get(url, params=params, timeout=10) as response:
            response.raise_for_status()
            payload: dict[str, Any] = await response.json()

        price_value = payload["result"]["index_price"]
        return Decimal(str(price_value))

    @staticmethod
    def _to_index_name(ticker: str) -> str:
        t = ticker.upper().strip()
        if t == "BTC":
            return "btc_usd"
        if t == "ETH":
            return "eth_usd"
        raise ValueError("ticker must be BTC or ETH")
