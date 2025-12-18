
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class PositionTypeEnum(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"

class PositionStatusEnum(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    PARTIAL = "PARTIAL"

class OpenPositionRequest(BaseModel):
    '''Request to open a new position'''

    symbol : str = Field(..., min_length=1, max_length=20)
    quantity : Decimal = Field(..., gt=0)
    entry_price: Decimal = Field(..., gt=0)
    postion_type : PositionTypeEnum = PositionTypeEnum.LONG

    @field_validator("symbol")
    def normalize_symbol(cls, v):
        return v.upper().strip()

class ClosePositionRequest(BaseModel):
    '''Request to close a position'''

    exit_price : Optional[Decimal] = Field(None, gt=0)
    quantity: Optional[Decimal] = Field(None, gt=0)

class PositionResponse(BaseModel):
    '''Position response schema'''

    id : UUID
    symbol: str
    quantity : Decimal
    entry_price : Decimal
    position_type : PositionTypeEnum
    status : PositionStatusEnum
    realized_pnl : Decimal
    created_at : datetime
    closed_at : Optional[datetime] = None

    # Calculated fields (added by service)
    current_price : Optional[float] = None
    unrealized_pnl : Optional[float] = None
    pnl_percentage : Optional[float] = None

    class Config:
        from_attributes = True

class PositionWithPnL(PositionResponse):
    '''Postion with realtime PnL data'''

    current_price : float
    unrealized_pnl : float
    pnl_percentage : float

class PortfolioSummary(BaseModel):
    '''Portfolio summary with all positons and totals'''

    user_id : str
    postions : List[PositionWithPnL]
    total_positions : int
    total_invested : float
    total_current_value : float
    total_unrealized_pnl : float
    total_pnl_percentage : float
    timestamp : datetime

