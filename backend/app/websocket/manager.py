"""
WebSocket Connection Manager Module

This module manages all WebSocket connections for the real-time trading platform.
It handles connection lifecycle, subscription management, and message broadcasting
with high efficiency and thread safety.

Key Features:
- Multi-connection support per user (mobile + web simultaneously)
- Bidirectional symbol subscription mapping for O(1) lookups
- Thread-safe operations with async locks
- Automatic cleanup of dead connections
- Broadcasting with error handling and dead connection removal

Architecture:
- active_connections: Maps user_id -> set of WebSocket connections
- symbol_subscribers: Maps symbol -> set of user_ids (for price broadcasts)
- user_subscriptions: Maps user_id -> set of symbols (for cleanup)
- Async lock ensures thread-safe operations across concurrent requests
"""

from datetime import datetime
from zoneinfo import ZoneInfo
from app.core.config import settings
import asyncio
from collections import defaultdict
from fastapi import WebSocket

from app.schemas.websocket import WSMessageType


class ConnectionManager:
    """
    Manages WebSocket connections and subscription mappings for real-time trading data.
    
    This class provides a centralized way to handle multiple WebSocket connections
    per user, manage symbol subscriptions, and broadcast messages efficiently.
    
    Data Structures:
        active_connections: {user_id: {websocket1, websocket2, ...}}
            - Supports multiple devices per user (phone + laptop)
            - Uses set for O(1) add/remove operations
            
        symbol_subscribers: {symbol: {user_id1, user_id2, ...}}
            - Maps trading symbols to interested users
            - Enables efficient price update broadcasting
            - O(1) lookup for "who needs BTCUSDT updates?"
            
        user_subscriptions: {user_id: {symbol1, symbol2, ...}}
            - Maps users to their subscribed symbols
            - Used for cleanup when user disconnects
            - Maintains consistency with symbol_subscribers
    
    Thread Safety:
        All operations use async locks to prevent race conditions
        when multiple WebSocket connections are established/closed simultaneously.
    """
    
    def __init__(self):
        # Map user IDs to their active WebSocket connections
        # Using defaultdict(set) automatically creates empty sets for new users
        self.active_connections: dict[str, set[WebSocket]] = defaultdict(set)
        
        # Bidirectional mapping for efficient lookups:
        # symbol -> users interested in that symbol (for broadcasting)
        self.symbol_subscribers: dict[str, set[str]] = defaultdict(set)
        
        # user -> symbols they're subscribed to (for cleanup)
        self.user_subscriptions: dict[str, set[str]] = defaultdict(set)
        
        # Async lock for thread-safe operations
        # Prevents race conditions when connections are added/removed concurrently
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, user_id: str, max_per_user: int = 3) -> bool:
        """
        Accept a new WebSocket connection for a user.
        
        This method handles the WebSocket handshake and adds the connection
        to the active connections pool. It enforces a maximum number of
        connections per user to prevent abuse.
        
        Args:
            websocket: The WebSocket connection to accept
            user_id: Unique identifier for the user
            max_per_user: Maximum allowed connections per user (default: 3)
            
        Returns:
            bool: True if connection accepted, False if rejected
            
        Connection Limit:
            Users are limited to prevent resource exhaustion and potential abuse.
            Typical use case: user has phone app + web browser + tablet connected.
        """
        async with self._lock:
            # Check if user has too many connections already
            if len(self.active_connections[user_id]) >= max_per_user:
                await websocket.close(code=4000, reason="Max connections exceeded")
                return False
            
            # Accept the WebSocket connection
            await websocket.accept()
            
            # Add to active connections pool
            self.active_connections[user_id].add(websocket)
            
            print(f"✅ User {user_id} connected. Total connections: {len(self.active_connections[user_id])}")
            return True

    async def disconnect(self, websocket: WebSocket, user_id: str):
        """
        Handle WebSocket disconnection and cleanup.
        
        This method removes the WebSocket from active connections and
        performs cleanup of subscription mappings if the user has no
        remaining connections.
        
        Args:
            websocket: The WebSocket connection being closed
            user_id: Unique identifier for the user
            
        Cleanup Process:
            1. Remove WebSocket from active connections
            2. If user has no more connections, clean up all subscriptions
            3. Remove empty entries from data structures to prevent memory leaks
        """
        async with self._lock:
            # Remove the WebSocket from active connections
            self.active_connections[user_id].discard(websocket)
            
            # If user has no more connections, clean up completely
            if not self.active_connections[user_id]:
                # Remove user from active connections
                del self.active_connections[user_id]
                
                # Clean up all symbol subscriptions for this user
                for symbol in list(self.user_subscriptions.get(user_id, [])):
                    # Remove user from symbol's subscriber list
                    self.symbol_subscribers[symbol].discard(user_id)
                    
                    # Remove empty symbol entries to prevent memory leaks
                    if not self.symbol_subscribers[symbol]:
                        del self.symbol_subscribers[symbol]
                
                # Remove user's subscription tracking
                if user_id in self.user_subscriptions:
                    del self.user_subscriptions[user_id]
                
                print(f"🔌 User {user_id} fully disconnected and cleaned up")
            else:
                print(f"🔌 User {user_id} connection closed. Remaining: {len(self.active_connections[user_id])}")

    async def subscribe(self, user_id: str, symbols: list[str]):
        """
        Subscribe a user to receive price updates for specific trading symbols.
        
        This method updates both the user->symbols and symbol->users mappings
        to enable efficient broadcasting when prices change.
        
        Args:
            user_id: Unique identifier for the user
            symbols: List of trading pair symbols (e.g., ["BTCUSDT", "ETHUSDT"])
            
        Bidirectional Mapping:
            - user_subscriptions[user_id] tracks what symbols user wants
            - symbol_subscribers[symbol] tracks which users want that symbol
            - Both are updated atomically to maintain consistency
        """
        async with self._lock:
            for symbol in symbols:
                # Normalize symbol to uppercase for consistency
                symbol = symbol.upper()
                
                # Add symbol to user's subscription list
                self.user_subscriptions[user_id].add(symbol)
                
                # Add user to symbol's subscriber list
                self.symbol_subscribers[symbol].add(user_id)
            
            print(f"📊 User {user_id} subscribed to {len(symbols)} symbols: {symbols}")

    async def unsubscribe(self, user_id: str, symbols: list[str]):
        """
        Unsubscribe a user from price updates for specific trading symbols.
        
        This method removes the user from subscription mappings for the
        specified symbols while maintaining data structure consistency.
        
        Args:
            user_id: Unique identifier for the user
            symbols: List of trading pair symbols to unsubscribe from
            
        Cleanup:
            - Removes entries from both mapping directions
            - Cleans up empty entries to prevent memory leaks
            - Maintains consistency between user_subscriptions and symbol_subscribers
        """
        async with self._lock:
            for symbol in symbols:
                symbol = symbol.upper()
                
                # Remove symbol from user's subscription list
                self.user_subscriptions[user_id].discard(symbol)
                
                # Remove user from symbol's subscriber list
                self.symbol_subscribers[symbol].discard(user_id)
                
                # Clean up empty entries
                if not self.symbol_subscribers[symbol]:
                    del self.symbol_subscribers[symbol]
            
            # Clean up user's subscription list if empty
            if not self.user_subscriptions[user_id]:
                del self.user_subscriptions[user_id]
            
            print(f"📊 User {user_id} unsubscribed from {len(symbols)} symbols: {symbols}")

    async def send_to_user(self, user_id: str, message: dict):
        """
        Send a message to all of a user's active WebSocket connections.
        
        This method handles sending messages to users who may have multiple
        devices connected simultaneously. It also handles connection failures
        by automatically cleaning up dead connections.
        
        Args:
            user_id: Unique identifier for the user
            message: Dictionary containing the message data to send
            
        Error Handling:
            - Catches WebSocket send failures (connection closed, network issues)
            - Automatically removes dead connections from active pool
            - Continues sending to remaining healthy connections
        """
        connections = self.active_connections.get(user_id, set())
        if not connections:
            return  # User not connected
        
        # Track connections that fail to send (dead connections)
        dead_connections = set()
        
        # Attempt to send message to all user's connections
        for websocket in connections:
            try:
                await websocket.send_json(message)
            except Exception as e:
                # Connection is dead - mark for removal
                print(f"⚠️ Dead connection detected for user {user_id}: {e}")
                dead_connections.add(websocket)
        
        # Clean up dead connections
        if dead_connections:
            for dead_ws in dead_connections:
                await self.disconnect(dead_ws, user_id)

    async def broadcast_price(self, symbol: str, price_data: dict):
        """
        Broadcast price update to all users subscribed to a trading symbol.
        
        This method efficiently finds all users interested in a specific symbol
        and sends them the price update. It's called when new price data
        arrives from the Binance WebSocket feed.
        
        Args:
            symbol: Trading pair symbol (e.g., "BTCUSDT")
            price_data: Dictionary containing price, volume, change data
            
        Message Format:
            {
                "type": "price_update",
                "data": {
                    "symbol": "BTCUSDT",
                    "price": 67234.50,
                    "volume": 1234.56,
                    "change_24h": 2.34,
                    "timestamp": "2024-01-01T12:00:00Z"
                }
            }
        """
        # Find all users subscribed to this symbol
        subscribers = self.symbol_subscribers.get(symbol, set())
        if not subscribers:
            return  # No one is interested in this symbol
        
        # Construct the price update message
        message = {
            "type": WSMessageType.PRICE_UPDATE,
            "data": {
                "symbol": symbol,
                **price_data,
                "timestamp": datetime.now(tz=ZoneInfo("UTC")).isoformat()
            }
        }
        
        # Send to all subscribers concurrently
        # Using gather with return_exceptions=True prevents one failure from stopping others
        tasks = [self.send_to_user(user_id, message) for user_id in subscribers]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def broadcast_pnl(self, user_id: str, pnl_data: dict):
        """
        Send P&L (Profit & Loss) update to a specific user.
        
        This method sends updated portfolio P&L calculations to a user
        when their positions are affected by price changes.
        
        Args:
            user_id: Unique identifier for the user
            pnl_data: Dictionary containing portfolio P&L calculations
            
        Message Format:
            {
                "type": "pnl_update",
                "data": {
                    "positions": [...],
                    "total_unrealized_pnl": 1234.56,
                    "total_pnl_percentage": 5.67,
                    "timestamp": "2024-01-01T12:00:00Z"
                }
            }
        """
        message = {
            "type": WSMessageType.PNL_UPDATE,
            "data": pnl_data
        }
        await self.send_to_user(user_id, message)

    def get_symbol_subscribers(self, symbol: str) -> set[str]:
        """
        Get all user IDs subscribed to a specific trading symbol.
        
        This method provides read-only access to the subscription mapping
        for use by other services (like the price update worker).
        
        Args:
            symbol: Trading pair symbol to query
            
        Returns:
            set[str]: Set of user IDs subscribed to the symbol
        """
        return self.symbol_subscribers.get(symbol.upper(), set()).copy()

    def get_connected_users(self) -> set[str]:
        """
        Get all currently connected user IDs.
        
        Returns:
            set[str]: Set of user IDs with active WebSocket connections
        """
        return set(self.active_connections.keys())

    def get_stats(self) -> dict:
        """
        Get connection and subscription statistics for monitoring.
        
        This method provides metrics useful for:
        - Health checks and monitoring
        - Load balancer decisions
        - Performance optimization
        - Debugging connection issues
        
        Returns:
            dict: Statistics including user counts, connections, and subscriptions
        """
        return {
            "connected_users": len(self.active_connections),
            "total_connections": sum(len(connections) for connections in self.active_connections.values()),
            "tracked_symbols": len(self.symbol_subscribers),
            "total_subscriptions": sum(len(subscribers) for subscribers in self.symbol_subscribers.values()),
            "avg_connections_per_user": (
                sum(len(connections) for connections in self.active_connections.values()) / 
                len(self.active_connections) if self.active_connections else 0
            )
        }


# Global singleton instance for application-wide use
# This ensures all parts of the application use the same connection manager
ws_manager = ConnectionManager()