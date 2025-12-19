
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

from pydantic import BaseModel



class WSMessageType(str, Enum):
    """
    Enumeration of WebSocket message types for client-server communication.
    
    This enum defines all possible message types that can be sent between
    the client and server over WebSocket connections. It ensures type safety
    and provides a centralized definition of the communication protocol.
    
    Client -> Server Messages:
        SUBSCRIBE: Request to receive price updates for specific symbols
        UNSUBSCRIBE: Request to stop receiving updates for symbols  
        GET_PORTFOLIO: Request current portfolio snapshot
        PONG: Response to server ping (keepalive)
        
    Server -> Client Messages:
        PRICE_UPDATE: Real-time price change notification
        PNL_UPDATE: Portfolio P&L recalculation result
        PORTFOLIO_SNAPSHOT: Complete portfolio state
        SUBSCRIBED/UNSUBSCRIBED: Confirmation of subscription changes
        PING: Keepalive message requiring pong response
        ERROR: Error message with details
    """
    # Client -> Server message types
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"  # FIXED: Was "unsuscribe" - corrected spelling
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
    """
    Schema for real-time price update messages sent via WebSocket.
    
    This model represents the structure of price data broadcasted to clients
    when market prices change. It includes current price, trading volume,
    and 24-hour change statistics.
    
    Attributes:
        symbol: Trading pair symbol (e.g., "BTCUSDT", "ETHUSDT")
        price: Current market price as a float
        volume: 24-hour trading volume (optional, may not be available for all sources)
        change_24h: 24-hour price change percentage (optional)
        timestamp: When this price update was generated
    """
    symbol: str
    price: float
    volume: Optional[float] = None  # FIXED: Was "volumn" - corrected spelling
    change_24h: Optional[float] = None
    timestamp: datetime

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
    