"""
FastAPI Dependencies Module

This module provides dependency injection functions for FastAPI routes.
Dependencies handle common operations like database session management,
repository instantiation, and user authentication.

Key Features:
- Repository pattern implementation with automatic session management
- JWT-based authentication with Redis session validation
- Type-safe dependency injection for better IDE support and runtime safety
"""

from typing import Optional
from uuid import UUID
from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

# Import exception classes for authentication errors
from app.core.exceptions import UnauthorizedException

# Import database connection utilities
from app.db.database import get_db
from app.db.redis import RedisClient, get_redis

# Import repository classes for data access layer
from app.repositories.user_repository import UserRepository
from app.repositories.position_repository import PositionRepository  
from app.repositories.trade_repository import TradeRepository

async def get_user_repo(db : AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

async def get_position_repo(db : AsyncSession = Depends(get_db)) -> PositionRepository:
    return PositionRepository(db)

async def get_trade_repo(db : AsyncSession = Depends(get_db)) -> TradeRepository:
    return TradeRepository(db)

async def get_current_user_id(
        authorization : Optional[str] = Header(None),
        redis: RedisClient = Depends(get_redis),
) -> UUID :
    if not authorization:
        raise UnauthorizedException("Missing authorization header")
    try:
        scheme, session_id = authorization.split(" ", 1)
        '''
        authorization = "Bearer abc123xyz"
        scheme, session_id = authorization.split(" ", 1)
        print(scheme)     # "Bearer"
        print(session_id) # "abc123xyz"
        '''

        if scheme.lower() != 'bearer':
            raise UnauthorizedException("Invalid auth scheme")
    except:
        raise UnauthorizedException("Invalid authorization format")

    session_data = await redis.get_session(session_id=session_id)
    if not session_data:
        raise UnauthorizedException("Invalid or expired session")
    
    return UUID(session_data["user_id"])
