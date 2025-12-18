from datetime import datetime
from zoneinfo import ZoneInfo
from app.core.config import settings
import asyncio
from collections import defaultdict
from fastapi import WebSocket

from app.schemas.websocket import WSMessageType


class ConnectionManager:
    def __init__(self):
        self.active_connections : dict[str, set[WebSocket]] = defaultdict(set)
        '''
        defaultdict(set)
        If a key doesn’t exist:

        Python automatically creates an empty set()

        No need to check for key existence
        '''
        self.symbol_subscribers : dict[str, set[str]] = defaultdict(set) #symbol -> set[userid]
        self.user_subscriptions : dict[str, set[str]] = defaultdict(set) #userid -> set[symbols]
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, user_id : str, max_per_user : int = 3) -> bool:
        async with self._lock:
            if len(self.active_connections[user_id]) >= max_per_user:
                await websocket.close(code=4000, reason="Max connections exceeded")
                return False
            
            await websocket.accept()
            self.active_connections[user_id].add(websocket)
            return True

    async def disconnect(self, websocket: WebSocket, user_id : str):
        async with self._lock:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
            
            for symbol in list(self.user_subscriptions.get(user_id, [])):
                self.symbol_subscribers[symbol].discard(user_id)
                if not self.symbol_subscribers[symbol]:
                    del self.symbol_subscribers[symbol]
            
            if user_id in self.user_subscriptions:
                del self.user_subscriptions[user_id]
    

    async def subscribe(self, user_id: str, symbols: list[str]):
        async with self._lock:
            for symbol in symbols:
                self.user_subscriptions[user_id].add(symbol)
                self.symbol_subscribers[symbol].add(user_id)

    async def unsubscribe(self, user_id: str, symbols: list[str]):
        async with self._lock:
            for symbol in symbols:
                self.user_subscriptions[user_id].discard(symbol)
                if len(self.user_subscriptions[user_id]) == 0:
                    self.user_subscriptions.pop(user_id)

                self.symbol_subscribers[symbol].discard(user_id)
                if len(self.symbol_subscribers[symbol]) == 0:
                    self.symbol_subscribers.pop(symbol)
    
    async def send_to_user(self, user_id: str, message: dict):
        connections = self.active_connections.get(user_id, [])
        dead = set()
        for ws in connections:
            try:
                await ws.send_json(message)
            except Exception:
                dead.add(ws)
        
        for ws in dead:
            await self.disconnect(ws, user_id)
    
    async def broadcast_price(self, symbol: str, price_data: dict):
        subscribers = self.symbol_subscribers.get(symbol, [])
        message = {
            "type" : WSMessageType.PRICE_UPDATE,
            "data" : {"symbol": symbol, **price_data, "timestamp": datetime.now(tz=ZoneInfo("UTC")).isoformat()}
        }
            
        tasks = [self.send_to_user(uid, price_data) for uid in subscribers]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def broadcast_pnl(self, user_id: str, pnl_data: dict):
        message = {
            "type" : WSMessageType.PNL_UPDATE,
            "data" : pnl_data
        }
        await self.send_to_user(user_id, message)

    def get_symbol_subscribers(self, symbol:str) -> set[str]:
        return self.symbol_subscribers[symbol]

    def get_connected_users(self) -> set[str]:
        return set(self.active_connections.keys())
    
    def get_stats(self) -> dict:
        return {
            "connected_users" : len(self.active_connections),
            "total_connections" : sum(len(c) for c in self.active_connections.values()),
            "tracked_symbols" : len(self.symbol_subscribers.keys()),
            "total_subscriptions" : sum(len(s) for s in self.symbol_subscribers.values())
        }

ws_manager = ConnectionManager()