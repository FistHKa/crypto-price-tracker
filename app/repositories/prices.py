from __future__ import annotations

from decimal import Decimal
from datetime import datetime
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.price import Price


async def create_price(
        db: AsyncSession,
        *,
        ticker: str,
        price: Decimal,
) -> Price:
    """
    Save a new price row and return the created ORM object.
    """
    row = Price(
        ticker=ticker.upper(),
        price=price,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


async def get_latest_price(
        db: AsyncSession,
        *,
        ticker: str,
) -> Price | None:
    stmt = (
        select(Price)
        .where(Price.ticker == ticker.upper())
        .order_by(Price.timestamp.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    return result.scalars().first()


async def list_prices(
        db: AsyncSession,
        *,
        ticker: str,
        limit: int = 1000,
        offset: int = 0,
) -> Sequence[Price]:
    stmt = (
        select(Price)
        .where(Price.ticker == ticker.upper())
        .order_by(Price.timestamp.asc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def list_prices_by_data(
        db: AsyncSession,
        *,
        ticker: str,
        date_from: datetime | None,
        date_to: datetime | None,
        limit: int = 1000,
        offset: int = 0,
) -> Sequence[Price]:
    stmt = select(Price).where(Price.ticker == ticker.upper())

    if date_from is not None:
        stmt = stmt.where(Price.timestamp >= date_from)
    if date_to is not None:
        stmt = stmt.where(Price.timestamp <= date_to)

    stmt = stmt.order_by(Price.timestamp.asc()).limit(limit).offset(offset)
    result = await db.execute(stmt)
    return result.scalars().all()
