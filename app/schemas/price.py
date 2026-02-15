from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_serializer


class PriceOut(BaseModel):
    id: int
    ticker: str
    price: Decimal
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("price")
    def serialize_price(self, v: Decimal) -> float:
        return float(v.normalize())
