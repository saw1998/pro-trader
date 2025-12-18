

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import router
from app.db.redis import redis_client
from app.db.database import db
from app.websocket.handlers import websocket_endpoint
from app.workers.binance_consumer import binance_consumer 
from app.core.config import settings
from app.websocket.manager import ws_manager


@asynccontextmanager
async def lifespan(app : FastAPI):
    # startup
    await redis_client.connect()
    await db.create_tables()

    asyncio.create_task(binance_consumer.listen())
    await binance_consumer.subscribe(["BTCUSDT", "ETHUSDT", "BNBUSDT"])

    yield

    # shutdown
    await binance_consumer.stop()
    await redis_client.disconnect()
    await db.close()

app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:3000"],
    allow_credentials = True,
    allow_methods=["*"],
    allow_headers = ["*"]
)

app.include_router(router)

@app.websocket("/ws")
async def ws_route(websocket, session_id : str):
    await websocket_endpoint(websocket=websocket, session_id=session_id)

@app.get("/health")
async def health():
    return {
        "status" : "healthy",
        "websocket" : ws_manager.get_stats()
    }