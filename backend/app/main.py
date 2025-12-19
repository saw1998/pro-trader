

"""
Main FastAPI Application Module

This is the entry point for the Pro Trader real-time trading platform.
It configures the FastAPI application with all necessary middleware,
database connections, WebSocket endpoints, and background workers.

Key Features:
- Real-time price streaming from Binance WebSocket API
- Redis-based caching and session management  
- PostgreSQL for persistent data storage
- WebSocket connections for live client updates
- Background workers for price data processing
- CORS middleware for frontend integration

Architecture:
- Async/await throughout for high concurrency
- Repository pattern for clean data access
- Service layer for business logic
- WebSocket manager for connection handling
- Background tasks for price buffering and P&L calculations
"""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket  # Added WebSocket import
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import router
from app.db.redis import redis_client
from app.db.database import db
from app.websocket.handlers import websocket_endpoint
from app.workers.binance_consumer import binance_consumer 
from app.core.config import settings
from app.websocket.manager import ws_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown procedures.
    
    This async context manager handles the complete lifecycle of the application,
    ensuring proper initialization of all services during startup and graceful
    cleanup during shutdown.
    
    Startup Sequence:
    1. Connect to Redis for caching and session management
    2. Create database tables if they don't exist (development convenience)
    3. Start Binance WebSocket consumer for real-time price data
    4. Subscribe to initial set of trading pairs for price streaming
    
    Shutdown Sequence:
    1. Stop Binance WebSocket consumer and close connection
    2. Disconnect from Redis and close connection pool
    3. Close database connection pool and cleanup resources
    
    This ensures no resource leaks and proper cleanup on application termination.
    """
    # === STARTUP PHASE ===
    print("🚀 Starting Pro Trader application...")
    
    # Initialize Redis connection pool for caching and sessions
    # Redis handles: price cache, user sessions, P&L cache, pub/sub messaging
    await redis_client.connect()
    print("✅ Redis connected")
    
    # Create database tables if they don't exist (useful for development)
    # In production, this would typically be handled by migration scripts
    await db.create_tables()
    print("✅ Database tables ready")

    # Start background task for Binance WebSocket price streaming
    # This runs continuously to fetch real-time market data
    asyncio.create_task(binance_consumer.listen())
    print("✅ Binance WebSocket consumer started")
    
    # Subscribe to initial trading pairs for price data
    # These are the most popular pairs - more can be added dynamically
    await binance_consumer.subscribe(["BTCUSDT", "ETHUSDT", "BNBUSDT"])
    print("✅ Subscribed to initial trading pairs")
    
    print("🎯 Application startup complete!")

    # === APPLICATION RUNNING ===
    # Yield control back to FastAPI - application is now serving requests
    yield

    # === SHUTDOWN PHASE ===
    print("🛑 Shutting down Pro Trader application...")
    
    # Stop Binance WebSocket consumer and close connection gracefully
    await binance_consumer.stop()
    print("✅ Binance WebSocket consumer stopped")
    
    # Close Redis connection pool and cleanup resources
    await redis_client.disconnect()
    print("✅ Redis disconnected")
    
    # Close database connection pool
    await db.close()
    print("✅ Database connections closed")
    
    print("👋 Application shutdown complete!")

# Create the main FastAPI application instance
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Real-time trading platform with WebSocket streaming and portfolio management",
    lifespan=lifespan  # Attach our startup/shutdown lifecycle manager
)

# Configure CORS middleware for frontend integration
# This allows the React frontend to make requests to our API
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # Use settings instead of hardcoded values
    allow_credentials=True,  # Allow cookies and authorization headers
    allow_methods=["*"],     # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"]      # Allow all headers (Authorization, Content-Type, etc.)
)

# Include all API routes under /api/v1 prefix
# This includes authentication, positions, trades, and other endpoints
app.include_router(router)

@app.websocket("/ws")
async def ws_route(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time trading data streaming.
    
    This endpoint handles WebSocket connections from authenticated clients,
    providing real-time price updates and portfolio P&L calculations.
    
    Connection Flow:
    1. Client connects with session_id as query parameter
    2. Server validates session against Redis
    3. If valid, accepts connection and starts streaming
    4. Client receives real-time price updates and P&L changes
    
    Args:
        websocket: FastAPI WebSocket connection instance
        session_id: User's session identifier for authentication
        
    URL Format: ws://localhost:8000/ws?session_id=<session_token>
    
    Message Types:
        - price_update: Real-time market price changes
        - pnl_update: Portfolio profit/loss recalculations  
        - portfolio_snapshot: Complete portfolio state
        - ping/pong: Connection keepalive
    """
    await websocket_endpoint(websocket=websocket, session_id=session_id)

@app.get("/health")
async def health():
    """
    Health check endpoint for monitoring and load balancer probes.
    
    This endpoint provides system health information including:
    - Overall application status
    - WebSocket connection statistics
    - Active user counts and connection metrics
    
    Used by:
    - Load balancers to determine if instance is healthy
    - Monitoring systems for alerting
    - DevOps teams for troubleshooting
    
    Returns:
        dict: Health status and WebSocket statistics
    """
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "websocket_stats": ws_manager.get_stats()
    }