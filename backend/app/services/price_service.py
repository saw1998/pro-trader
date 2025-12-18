
from typing import Optional
from app.db.redis import RedisClient


class PriceService:
    def __init__(self, redis: RedisClient):
        self.redis = redis
    
    async def get_price(self, symbol: str) -> Optional[float]:
        return await self.redis.get_price(symbol=symbol.upper())
    
    async def get_prices(self, symbols: list[str]) -> dict[str, Optional[float]]:
        return await self.redis.get_prices_bulk([s.upper() for s in symbols])

    async def update_prices(self, prices: dict[str, float]) -> None:
        await self.redis.set_prices_bulk(prices)

    async def get_subscribers(self, symbol: str) -> set[str]:
        return await self.redis.get_symbol_subscribers(symbol.upper())
