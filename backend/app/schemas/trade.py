
from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class TradeSideEnum(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

class TradeResponse(BaseModel):
    id : UUID
    symbol : str
    side : TradeSideEnum
    quantity : Decimal
    price : Decimal
    total_value : Decimal
    fee : Decimal
    realized_pnl : Decimal
    executed_at : datetime

    class Config:
        from_attributes = True

    
