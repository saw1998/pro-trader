from typing import Optional
from uuid import UUID
from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import UnauthorizedException
from app.db import get_db, RedisClient, get_redis
from app.repositories import UserRepository, PositionRepository, TradeRepository

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
