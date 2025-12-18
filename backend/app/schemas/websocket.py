
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

from pydantic import BaseModel



class WSMessageType(str, Enum):
    # client -> server

    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsuscribe"
    GET_PORTFOLIO = "get_portfolio"
    PONG = "pong"

    # server -> client
    PRICE_UPDATE = "price_update"
    PNL_UPDATE = "pnl_update"
    PORTFOLIO_SNAPSHOT = "portfolio_snapshot"
    SUBSCRIBED = "subscribed"
    UNSUBSCRIBED = "unsubscribed"
    PING = "ping"
    ERROR = "error"

class WSMessage(BaseModel):
    type : WSMessageType
    data : Optional[Any] = None
    message : Optional[Any] = None

class PriceUpdate(BaseModel):
    symbol : str
    price : float
    volumn : Optional[float] = None
    change_24h : Optional[float] = None
    timestamp : datetime

class PnLUpdate(BaseModel):
    positions : list[dict]
    total_unrealized_pnl : float
    total_unrealized_percentage : float
    timestamp : datetime

# class WSClientMessage(BaseModel):
#     '''Message from client'''

#     type: WSMessageType
#     symbols : Optional[List[str]] = None
#     data : Optional[Dict[str, Any]] = None

# class WSServerMessage(BaseModel):
#     '''Message to client'''

#     type : WSMessageType
#     data : Optional[Dict[str, Any]] = None
#     message : Optional[str] = None
#     timestamp : Optional[datetime] = None

#     def __init__(self, **data):
#         if "timestamp" not in data:
#             data["timestamp"] = datetime.now(tz=ZoneInfo("UTC"))
#         super().__init__(**data)

# class PriceUpdate(BaseModel):
#     '''price update data'''

#     symbol : str
#     price : float
#     volumn : Optional[float] = None
#     change_24h : Optional[float] = None
#     timestamp : datetime
    