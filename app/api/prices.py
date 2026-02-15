from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.prices import get_latest_price, list_prices, list_prices_by_data
from app.schemas.price import PriceOut

router = APIRouter(
    prefix="/prices",
    tags=["prices"],
)


@router.get(
    "/",
    response_model=list[PriceOut],
)
async def all_prices(
    ticker: str = Query(..., description="Ticker: BTC or ETH"),
    limit: int = Query(1000, ge=1, le=5000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    return await list_prices(db, ticker=ticker, limit=limit, offset=offset)


@router.get(
    "/latest",
    response_model=PriceOut,
)
async def latest_price(
    ticker: str = Query(..., description="Ticker: BTC or ETH"),
    db: AsyncSession = Depends(get_db),
):
    row = await get_latest_price(db, ticker=ticker)
    if row is None:
        raise HTTPException(
            status_code=404, detail="No data for this ticker yet")
    return row


@router.get(
    "/by-date",
    response_model=list[PriceOut],
)
async def prices_by_date(
    ticker: str = Query(..., description="Ticker: BTC or ETH"),
    date_from: datetime | None = Query(
        None, description="ISO datetime, e.g. 2022-10-25T00:00:00Z"),
    date_to: datetime | None = Query(
        None, description="ISO datetime, e.g. 2022-10-25T00:00:00Z"),
    limit: int = Query(1000, ge=1, le=5000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    return await list_prices_by_data(
        db,
        ticker=ticker,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset,
    )
