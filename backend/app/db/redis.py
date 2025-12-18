import json
import redis.asyncio as redis
from typing import Dict, List, Optional, Set
from app.core.config import settings


class RedisClient:
    '''Async redis client with helper methods'''

    def __init__(self):
        self.pool : redis.ConnectionPool
        self.client : redis.Redis

    async def connect(self):
        '''Initialize Redis connection pool'''
        self.pool : redis.ConnectionPool = redis.ConnectionPool.from_url(
            settings.REDIS_URL,
            max_connections=settings.REDIS_POOL_SIZE,
            decode_responses=True
        )
        self.client = redis.Redis(connection_pool=self.pool)

        # Test connection
        await self.client.ping()
        print("redis connected")

    async def disconnect(self):
        '''Close Redis connection'''
        if self.client:
            await self.client.aclose()
        if self.pool:
            await self.pool.disconnect()
        print("Redis disconnected")


    # ===== Basic operations =========

    async def get(self, key: str) -> Optional[str]:
        '''getting string value'''
        if self.client:
            return await self.client.get(key)
        return None
    
    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        '''set string value with optional ttl'''
        if ttl:
            return await self.client.setex(key, ttl, value)
        return await self.client.set(key, value)

    async def delete(self, *keys: str) -> int:
        '''delete keys'''
        if keys:
            return await self.client.delete(*keys)
        return 0

    async def exists(self, key: str) -> bool:
        '''check if key exist'''
        return await self.client.exists(key) > 0 

    async def expire(self, key: str, ttl:int) -> bool:
        '''set expiration on key'''
        return await self.client.expire(key, ttl)

    async def ttl(self, key:str) -> int:
        return await self.client.ttl(key)
    
    # ========== Json operations =========================

    async def get_json(self, key: str) -> Optional[Dict]:
        data = await self.client.get(key)
        if data:
            return json.loads(data)
        return None

    async def set_json(self, key: str, value : Dict, ttl: Optional[int] = None) -> bool:
        data = json.dumps(value)
        return await self.client.set(key, data, ttl)

    # =========== Hash operations ===================

    async def hget(self, key, field:str) -> Optional[str] :
        '''get hash field'''
        return await self.client.hget(key, field)
    
    async def hset(self, key, field: str, value: str) -> int:
        '''set hash field'''
        return await self.client.hset(key, field, value)

    async def hmset(self, key: str, mapping:Dict[str, str]) -> bool:
        '''set multiple hash fields'''
        return await self.client.hset(key, mapping=mapping)

    async def hgetall(self, key:str) -> Dict[str, str]:
        '''get all hash field'''
        return await self.client.hgetall(key)
    
    async def hdel(self, key:str, *fields: str) -> int:
        '''delete hash filed'''
        return await self.client.hdel(key, *fields)


    # ========= set operations =======================

    async def sadd(self, key:str, *values:str) -> int:
        '''add to set'''
        if values:
            return await self.client.sadd(key, *values)
        return 0

    async def srem(self, key: str, *values: str) -> int:
        '''remove from set'''
        if values:
            return await self.client.srem(key, *values)
        return 0

    async def smembers(self, key:str) -> Set[str]:
        '''get all set members'''
        return await self.client.smembers(key)

    async def sismember(self, key: str, value:str) -> bool:
        return await self.client.sismember(key, value)

    # =========== Pub/Sub Operations =========================
    
    async def publish(self, channel:str, message: str) -> int:
        '''publish message to channel'''
        return await self.client.publish(channel, message)

    async def publish_json(self, channel: str, data:Dict) -> int:
        return await self.client.publish(channel, json.dumps(data))

    async def pubsub(self):
        '''get pubsub instances'''
        return self.client.pubsub()


    # ========== Pipeline Operations ==================
    
    def pipeline(self):
        '''get pipeline for batch operatations'''
        return self.client.pipeline()

    # ============ Price Specific Operations ============

    async def set_price(self, symbol: str, price: float, ttl:int = 60):
        '''set current price for symbol'''
        key = f"price:{symbol}"
        await self.set(key, str(price), ttl)

    async def get_price(self, symbol: str) -> Optional[float]:
        '''get current price for symbol'''
        key = f"price:{symbol}"
        value = await self.get(key)
        return float(value) if value else None

    async def set_prices_bulk(self, prices: Dict[str, float], ttl:int=60):
        '''set multiple price atomically'''
        pipe = self.pipeline()
        for symbol, price in prices.items():
            key = f"price:{symbol}"
            pipe.setex(key, ttl, str(price))
        await pipe.execute()

    async def get_prices_bulk(self, symbols: List[str]) -> Dict[str, Optional[float]]:
        '''get multiple prices'''
        if not symbols:
            return {}

        pipe = self.pipeline()
        for symbol in symbols:
            pipe.get(f"price:{symbol}")
        
        results = await pipe.execute()

        return {
            symbol: float(value) if value else None
            for symbol, value in zip(symbols, results)
        }

    # user session operations
    async def create_session(self, session_id : str, user_data : dict) -> None:
        key = f"session:{session_id}"
        await self.client.setex(key, settings.SESSION_EXPIRE_SECONDS, json.dumps(user_data))
    
    async def get_session(self, session_id: str) -> Optional[dict]:
        key = f"session:{session_id}"
        data = await self.client.get(key)
        if data:
            await self.client.expire(key, settings.SESSION_EXPIRE_SECONDS) #sliding expiration
            return json.loads(data)
        return None
    
    async def delete_session(self, session_id: str) -> None:
        await self.client.delete(f"session:{session_id}")

    async def delete_user_sessions(self, user_id: str) -> None:
        pattern = f"session:*"
        async for key in self.client.scan_iter(match=pattern):
            data = await self.get_session(key)
            if data:
                if data.get("user_id") == user_id:
                    await self.delete_session(key)
    
    # User-Symbol subscription tracking
    async def subscribe_user_to_symbol(self, user_id: str, symbol: str) -> None:
        pipe = self.client.pipeline()
        pipe.sadd(f"user_symbols:{user_id}", symbol)
        pipe.sadd(f"symbol_subscribers:{symbol}", user_id)
        await pipe.execute()

    async def unsubscribe_user_from_symbol(self, user_id: str, symbol:str)->None:
        pipe = self.client.pipeline()
        pipe.srem("user_symbols:{user_id}", symbol)
        pipe.srem("symbol_subscribers:{symbol}", user_id)
        await pipe.execute()

    async def get_symbol_subscribers(self, symbol:str) -> set[str]:
        return await self.client.smembers(f"symbol_subscribers:{symbol}")

    async def get_user_symbols(self, user_id: str) -> set[str]:
        return await self.client.smembers(f"user_symbols:{user_id}")

    # PnL cache
    async def cache_user_pnl(self, user_id: str, pnl_data: dict) -> None:
        await self.client.setex(f"pnl:{user_id}", settings.PNL_CACHE_TTL_SECONDS, json.dumps(pnl_data))
    
    async def get_user_pnl(self, user_id:str) -> Optional[dict]:
        data = await self.client.get("pnl:{user_id}")
        if data:
            return json.loads(data)
        return None
    
    async def invalidate_user_pnl(self, user_id: str) -> None:
        await self.client.delete(f"pnl:{user_id}")

    
    

'''
In a single Python process:
✅ Effectively a singleton

When this breaks (important)
1️⃣ Multiple processes (VERY common)

Each process has its own memory space.

Examples:

uvicorn --workers 4

gunicorn

Celery workers

multiprocessing

Kubernetes pods

➡️ Each process creates its own RedisClient()

This is usually fine for Redis (clients are lightweight), but it’s not a true global singleton.
'''

redis_client = RedisClient()

def get_redis() -> RedisClient:
    return redis_client