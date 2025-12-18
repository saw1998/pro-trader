import asyncio
from datetime import datetime
import json
from typing import Optional
from uuid import UUID
from zoneinfo import ZoneInfo
from websockets.client import WebSocketClientProtocol
import websockets
from app.db.redis import redis_client
from app.repositories.position_repository import PositionRepository
from app.services.pnl_service import PnLService
from app.websocket.manager import ws_manager
from app.db.database import db

class BinanceConsumer:
    def __init__(self):
        self.ws : Optional[WebSocketClientProtocol] = None
        self.subscribed_symbols : set[str] = set()
        self.running: bool = False
        self.reconnect_attempts : int = 0
        self.max_reconnect : int = 10
        self.ws_url = "wss://stream.binance.com:9443/ws"

        self.price_buffer : dict[str, dict] = {}
        self.buffer_interval : float = 0.1 #100ms
        self._buffer_task : Optional[asyncio.Task] = None
    
    async def connect(self) -> bool:
        try:
            self.ws = await websockets.connect(
                self.ws_url,
                ping_interval = 20,
                ping_timeout = 10
            )
            self.running = True
            self.reconnect_attempts = 0
            self._buffer_task = asyncio.create_task(self._flush_buffer_loop())
            return True
        except Exception:
            return False

    async def subscribe(self, symbols: list[str]):
        if not self.ws:
            await self.connect()
        assert(self.ws is not None)
        
        new_symbols = set(s.upper() for s in symbols) - self.subscribed_symbols
        if not new_symbols:
            return
        
        streams = [f"{s.lower()}@ticker" for s in new_symbols]
        msg = {"method": "SUBSCRIBE", "params": streams, "id":int(datetime.now(tz=ZoneInfo("UTC")).timestamp())}
        await self.ws.send(json.dumps(msg))
        self.subscribed_symbols.update(new_symbols) 

    async def unsubscribe(self, symbols: list[str]):
        if not self.ws:
            return
        assert(self.ws is not None)

        to_remove = set(s.upper() for s in symbols) & self.subscribed_symbols
        if not to_remove:
            return
        
        streams = [f"{s.lower()}@ticker" for s in to_remove]
        msg = {"method" : "UNSUBSCRIBE", "params": streams, "id":int(datetime.now(tz=ZoneInfo("UTC")).timestamp())}
        await self.ws.sent(json.dumps(msg))
        self.subscribed_symbols -= to_remove

    async def _process_message(self, message: str):
        try:
            data = json.loads(message)
            if "result" in data or "e" not in data:
                return
            
            if data["e"] == "24htTicker":
                symbol = data["s"].upper()
                self.price_buffer[symbol] = {
                    "price" : float(data["c"]),
                    "volumn" : float(data["v"]),
                    "change_24h" : float(data.get("P", 0)),
                    "high_24h" : float(data.get("h", 0)),
                    "low_24h" : float(data.get("l", 0))
                }
        except Exception:
            pass

    async def _flush_buffer_loop(self):
        while self.running:
            await asyncio.sleep(self.buffer_interval)
            if not self.price_buffer:
                continue

            buffer = self.price_buffer.copy()
            self.price_buffer.clear()

            try:
                await redis_client.set_prices_bulk(buffer) #TODO, check this

                affected_users : set[str] = set()
                for symbol in buffer:
                    subscribers = ws_manager.get_symbol_subscribers(symbol)
                    affected_users.update(subscribers)

                broadcast_tasks = [
                    ws_manager.broadcast_price(symbol, data)
                    for symbol, data in buffer.items()
                ]
                if broadcast_tasks:
                    await asyncio.gather(*broadcast_tasks, return_exceptions=True)
                
                if affected_users:
                    asyncio.create_task(self._update_pnl_for_users(affected_users))
            
            except Exception:
                pass

    async def _update_pnl_for_users(self, user_ids:set[str]):
        await asyncio.sleep(0.05) #Debounce

        try:
            async with db.session_factory() as session:
                position_repo = PositionRepository(session)
                pnl_service = PnLService(position_repo, redis_client)

                for user_id in user_ids:
                    try:
                        portfolio = await pnl_service.get_portfolio(UUID(user_id))
                        await ws_manager.broadcast_pnl(user_id, portfolio.model_dump())
                    except Exception:
                        pass

        except Exception:
            pass

    async def listen(self):
        while self.running:
            try:
                if not self.ws:
                    if not await self.connect():
                        await asyncio.sleep(5)
                        continue
                
                assert(self.ws is not None)
                async for message in self.ws:
                    await self._process_message(message)
            
            except websockets.exceptions.ConnectionClosed:
                self.ws = None
                await self._handle_reconnect()
            except Exception:
                self.ws = None
                await self._handle_reconnect()

    async def _handle_reconnect(self):
        if self.reconnect_attempts >= self.max_reconnect:
            self.running = False
            return
        
        wait = min(30, 2**self.reconnect_attempts)
        await asyncio.sleep(wait)
        self.reconnect_attempts += 1

        if await self.connect():
            symbols = list(self.subscribed_symbols)
            self.subscribed_symbols.clear()
            await self.subscribe(symbols)

    async def stop(self):
        self.running = False
        if self._buffer_task:
            self._buffer_task.cancel()
        if self.ws:
            await self.ws.close()

binance_consumer = BinanceConsumer()




