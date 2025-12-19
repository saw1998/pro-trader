"""
Binance WebSocket Consumer Module

This module handles real-time price data streaming from Binance's WebSocket API.
It manages subscriptions, processes incoming price data, buffers updates,
and broadcasts them to connected clients while calculating P&L for affected users.
"""

import asyncio
from datetime import datetime
import json
import logging
from typing import Optional
from uuid import UUID
from zoneinfo import ZoneInfo

# Updated imports for websockets v12.0+
# In v12+, the asyncio client is in websockets.asyncio.client
from websockets.asyncio.client import connect, ClientConnection
from websockets.exceptions import ConnectionClosed, ConnectionClosedError

from app.db.redis import redis_client
from app.repositories.position_repository import PositionRepository
from app.services.pnl_service import PnLService
from app.websocket.manager import ws_manager
from app.db.database import db

# Configure logger for this module
logger = logging.getLogger(__name__)


class BinanceConsumer:
    """
    Manages a persistent WebSocket connection to Binance's streaming API.
    
    This class handles:
    - Establishing and maintaining WebSocket connections with auto-reconnect
    - Subscribing/unsubscribing to symbol price streams
    - Buffering incoming price data to reduce broadcast frequency
    - Broadcasting price updates to connected clients
    - Triggering P&L recalculations for affected users
    
    Attributes:
        ws: The active WebSocket connection (None if disconnected)
        subscribed_symbols: Set of currently subscribed trading pair symbols
        running: Flag indicating if the consumer is active
        reconnect_attempts: Counter for consecutive reconnection attempts
        max_reconnect: Maximum allowed reconnection attempts before giving up
        ws_url: Binance WebSocket API endpoint URL
        price_buffer: Buffer storing latest price data before broadcast
        buffer_interval: Time interval (seconds) between buffer flushes
    """
    
    def __init__(self) -> None:
        """Initialize the Binance WebSocket consumer with default settings."""
        
        # WebSocket connection instance (None when disconnected)
        # Updated type hint for websockets v12+: ClientConnection replaces WebSocketClientProtocol
        self.ws: Optional[ClientConnection] = None
        
        # Set of uppercase symbol names we're currently subscribed to (e.g., "BTCUSDT")
        self.subscribed_symbols: set[str] = set()
        
        # Flag to control the main listening loop
        self.running: bool = False
        
        # Reconnection tracking
        self.reconnect_attempts: int = 0
        self.max_reconnect: int = 10
        
        # Binance WebSocket streaming endpoint
        self.ws_url: str = "wss://stream.binance.com:9443/ws"
        
        # Price data buffer - accumulates updates before broadcasting
        # Format: {symbol: {price, volume, change_24h, high_24h, low_24h}}
        self.price_buffer: dict[str, dict] = {}
        
        # Buffer flush interval in seconds (100ms for responsive updates)
        self.buffer_interval: float = 0.1
        
        # Background task reference for buffer flushing
        self._buffer_task: Optional[asyncio.Task] = None
    
    async def connect(self) -> bool:
        """
        Establish a WebSocket connection to Binance.
        
        Creates a new WebSocket connection with ping/pong keepalive settings.
        Also starts the background buffer flush task upon successful connection.
        
        Returns:
            bool: True if connection successful, False otherwise
            
        Note:
            In websockets v12+, `connect()` is used instead of `websockets.connect()`
            and returns a ClientConnection object.
        """
        try:
            # Establish WebSocket connection using the new asyncio client API
            # ping_interval: Send ping every 20 seconds to keep connection alive
            # ping_timeout: Wait up to 10 seconds for pong response
            # close_timeout: Wait up to 10 seconds for graceful close
            self.ws = await connect(
                self.ws_url,
                ping_interval=20,
                ping_timeout=10,
                close_timeout=10
            )
            
            # Mark consumer as running
            self.running = True
            
            # Reset reconnection counter on successful connect
            self.reconnect_attempts = 0
            
            # Start background task to periodically flush price buffer
            self._buffer_task = asyncio.create_task(self._flush_buffer_loop())
            
            logger.info("Successfully connected to Binance WebSocket")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Binance WebSocket: {e}")
            return False

    async def subscribe(self, symbols: list[str]) -> None:
        """
        Subscribe to price streams for the given trading pair symbols.
        
        Sends a SUBSCRIBE message to Binance for any new symbols not already
        subscribed. Uses the 24hr ticker stream for comprehensive price data.
        
        Args:
            symbols: List of trading pair symbols (e.g., ["BTCUSDT", "ETHUSDT"])
            
        Note:
            - Symbols are automatically converted to uppercase internally
            - Already-subscribed symbols are skipped to avoid duplicate subscriptions
        """
        # Ensure we have an active connection
        if not self.ws:
            connected = await self.connect()
            if not connected:
                logger.warning("Cannot subscribe: WebSocket connection failed")
                return
        
        # Type guard assertion for type checker
        assert self.ws is not None
        
        # Find symbols we haven't subscribed to yet
        # Convert to uppercase for consistency (Binance uses uppercase internally)
        new_symbols = set(s.upper() for s in symbols) - self.subscribed_symbols
        
        if not new_symbols:
            logger.debug("No new symbols to subscribe to")
            return
        
        # Build stream names - using ticker stream for 24hr price data
        # Format: symbol@ticker (e.g., "btcusdt@ticker")
        streams = [f"{s.lower()}@ticker" for s in new_symbols]
        
        # Construct Binance subscription message
        # id: Unique identifier for tracking responses (using UTC timestamp)
        msg = {
            "method": "SUBSCRIBE",
            "params": streams,
            "id": int(datetime.now(tz=ZoneInfo("UTC")).timestamp())
        }
        
        # Send subscription request
        await self.ws.send(json.dumps(msg))
        
        # Track newly subscribed symbols
        self.subscribed_symbols.update(new_symbols)
        logger.info(f"Subscribed to symbols: {new_symbols}")

    async def unsubscribe(self, symbols: list[str]) -> None:
        """
        Unsubscribe from price streams for the given trading pair symbols.
        
        Sends an UNSUBSCRIBE message to Binance for symbols we're currently
        subscribed to.
        
        Args:
            symbols: List of trading pair symbols to unsubscribe from
        """
        # Can't unsubscribe without a connection
        if not self.ws:
            logger.warning("Cannot unsubscribe: No active WebSocket connection")
            return
        
        # Type guard assertion
        assert self.ws is not None

        # Find symbols we're actually subscribed to that should be removed
        to_remove = set(s.upper() for s in symbols) & self.subscribed_symbols
        
        if not to_remove:
            logger.debug("No matching symbols to unsubscribe from")
            return
        
        # Build stream names for unsubscription
        streams = [f"{s.lower()}@ticker" for s in to_remove]
        
        # Construct Binance unsubscription message
        msg = {
            "method": "UNSUBSCRIBE",
            "params": streams,
            "id": int(datetime.now(tz=ZoneInfo("UTC")).timestamp())
        }
        
        # FIXED: Changed 'sent' to 'send' (typo in original code)
        await self.ws.send(json.dumps(msg))
        
        # Remove from tracked subscriptions
        self.subscribed_symbols -= to_remove
        logger.info(f"Unsubscribed from symbols: {to_remove}")

    async def _process_message(self, message: str) -> None:
        """
        Process a raw WebSocket message from Binance.
        
        Parses the JSON message and extracts relevant price data from
        24hr ticker events, storing them in the price buffer.
        
        Args:
            message: Raw JSON string received from WebSocket
            
        Note:
            Messages without event type or subscription confirmations
            (containing "result") are silently ignored.
        """
        try:
            data = json.loads(message)
            
            # Skip subscription confirmation messages (have "result" key)
            # and messages without event type ("e" key)
            if "result" in data or "e" not in data:
                return
            
            # Process 24hr ticker events
            if data["e"] == "24hrTicker":
                # Extract symbol in uppercase for consistency
                symbol = data["s"].upper()
                
                # Store price data in buffer
                # FIXED: Changed 'volumn' to 'volume' (spelling error)
                self.price_buffer[symbol] = {
                    "price": float(data["c"]),       # Current/close price
                    "volume": float(data["v"]),      # 24hr trading volume
                    "change_24h": float(data.get("P", 0)),  # 24hr price change %
                    "high_24h": float(data.get("h", 0)),    # 24hr high price
                    "low_24h": float(data.get("l", 0))      # 24hr low price
                }
                
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse WebSocket message: {e}")
        except KeyError as e:
            logger.warning(f"Missing expected field in message: {e}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")

    async def _flush_buffer_loop(self) -> None:
        """
        Background task that periodically flushes the price buffer.
        
        Runs continuously while the consumer is active, flushing buffered
        price data at regular intervals. This batches updates to reduce
        the frequency of Redis writes and WebSocket broadcasts.
        
        The flush process:
        1. Copies and clears the current buffer
        2. Stores prices in Redis for persistence/caching
        3. Broadcasts prices to subscribed WebSocket clients
        4. Triggers P&L recalculation for affected users
        """
        while self.running:
            # Wait for the specified interval before flushing
            await asyncio.sleep(self.buffer_interval)
            
            # Skip if no data buffered
            if not self.price_buffer:
                continue

            # Atomically copy and clear buffer to avoid race conditions
            buffer = self.price_buffer.copy()
            self.price_buffer.clear()

            try:
                # Persist price data to Redis for caching
                # This allows other services to access latest prices
                await redis_client.set_prices_bulk(buffer)

                # Collect all users subscribed to any of the updated symbols
                affected_users: set[str] = set()
                for symbol in buffer:
                    subscribers = ws_manager.get_symbol_subscribers(symbol)
                    affected_users.update(subscribers)

                # Create broadcast tasks for each symbol's price update
                broadcast_tasks = [
                    ws_manager.broadcast_price(symbol, data)
                    for symbol, data in buffer.items()
                ]
                
                # Execute all broadcasts concurrently
                # return_exceptions=True prevents one failure from canceling others
                if broadcast_tasks:
                    await asyncio.gather(*broadcast_tasks, return_exceptions=True)
                
                # Trigger P&L updates for users with positions in affected symbols
                # Run as separate task to not block buffer flushing
                if affected_users:
                    asyncio.create_task(self._update_pnl_for_users(affected_users))
            
            except Exception as e:
                logger.error(f"Error flushing price buffer: {e}")

    async def _update_pnl_for_users(self, user_ids: set[str]) -> None:
        """
        Recalculate and broadcast P&L updates for affected users.
        
        Fetches current portfolio data for each user and broadcasts
        the updated P&L information via WebSocket.
        
        Args:
            user_ids: Set of user ID strings to update
            
        Note:
            Includes a small debounce delay to batch rapid successive updates.
        """
        # Small debounce delay to batch rapid updates
        await asyncio.sleep(0.05)

        try:
            # Create a new database session for this operation
            async with db.session_factory() as session:
                # Initialize repositories and services
                position_repo = PositionRepository(session)
                pnl_service = PnLService(position_repo, redis_client)

                # Process each affected user
                for user_id in user_ids:
                    try:
                        # Fetch current portfolio with calculated P&L
                        portfolio = await pnl_service.get_portfolio(UUID(user_id))
                        
                        # Broadcast updated P&L to user's WebSocket connections
                        await ws_manager.broadcast_pnl(user_id, portfolio.model_dump())
                        
                    except ValueError as e:
                        # Invalid UUID format
                        logger.warning(f"Invalid user_id format: {user_id} - {e}")
                    except Exception as e:
                        # Log individual user errors but continue processing others
                        logger.error(f"Error updating P&L for user {user_id}: {e}")

        except Exception as e:
            logger.error(f"Error in P&L update batch: {e}")

    async def listen(self) -> None:
        """
        Main listening loop for WebSocket messages.
        
        Continuously listens for incoming messages and processes them.
        Handles disconnections with automatic reconnection attempts.
        
        This method runs indefinitely until `stop()` is called or
        maximum reconnection attempts are exceeded.
        """
        logger.info("Starting Binance WebSocket listener")
        
        while self.running:
            try:
                # Ensure we have an active connection
                if not self.ws:
                    if not await self.connect():
                        # Wait before retrying connection
                        await asyncio.sleep(5)
                        continue
                
                # Type guard assertion
                assert self.ws is not None
                
                # Iterate over incoming messages
                # In websockets v12+, the connection is an async iterator
                async for message in self.ws:
                    # Handle both string and bytes messages
                    if isinstance(message, bytes):
                        message = message.decode('utf-8')
                    await self._process_message(message)
            
            except ConnectionClosed as e:
                # Connection was closed (could be normal or error)
                logger.warning(f"WebSocket connection closed: {e}")
                self.ws = None
                await self._handle_reconnect()
                
            except ConnectionClosedError as e:
                # Connection closed with an error
                logger.error(f"WebSocket connection error: {e}")
                self.ws = None
                await self._handle_reconnect()
                
            except Exception as e:
                # Unexpected error - log and attempt reconnect
                logger.error(f"Unexpected error in WebSocket listener: {e}")
                self.ws = None
                await self._handle_reconnect()

    async def _handle_reconnect(self) -> None:
        """
        Handle reconnection logic with exponential backoff.
        
        Implements exponential backoff strategy for reconnection attempts,
        capped at 30 seconds. Stops attempting after max_reconnect failures.
        Upon successful reconnection, resubscribes to previously subscribed symbols.
        """
        # Check if we've exceeded maximum reconnection attempts
        if self.reconnect_attempts >= self.max_reconnect:
            logger.error(
                f"Maximum reconnection attempts ({self.max_reconnect}) exceeded. "
                "Stopping consumer."
            )
            self.running = False
            return
        
        # Calculate wait time with exponential backoff (capped at 30 seconds)
        wait = min(30, 2 ** self.reconnect_attempts)
        logger.info(
            f"Reconnection attempt {self.reconnect_attempts + 1}/{self.max_reconnect} "
            f"in {wait} seconds"
        )
        await asyncio.sleep(wait)
        
        # Increment attempt counter
        self.reconnect_attempts += 1

        # Attempt to reconnect
        if await self.connect():
            # Resubscribe to all previously subscribed symbols
            symbols = list(self.subscribed_symbols)
            
            # Clear subscription tracking (connect was successful, but need to resubscribe)
            self.subscribed_symbols.clear()
            
            # Resubscribe to all symbols
            if symbols:
                await self.subscribe(symbols)
                logger.info(f"Resubscribed to {len(symbols)} symbols after reconnection")

    async def stop(self) -> None:
        """
        Gracefully stop the WebSocket consumer.
        
        Cancels the buffer flush task and closes the WebSocket connection.
        Should be called during application shutdown.
        """
        logger.info("Stopping Binance WebSocket consumer")
        
        # Signal loops to stop
        self.running = False
        
        # Cancel the buffer flush background task
        if self._buffer_task:
            self._buffer_task.cancel()
            try:
                await self._buffer_task
            except asyncio.CancelledError:
                pass  # Expected when canceling
        
        # Close WebSocket connection gracefully
        if self.ws:
            await self.ws.close()
            logger.info("WebSocket connection closed")


# Global singleton instance for application-wide use
binance_consumer = BinanceConsumer()