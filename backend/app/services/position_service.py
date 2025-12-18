
from decimal import Decimal
from typing import Optional
from uuid import UUID
from app.core.exceptions import BadRequestException, NotFoundException
from app.db.redis import RedisClient
from app.models.positions import Position, PositionStatus, PositionType
from app.models.trade import TradeSide
from app.repositories.position_repository import PositionRepository
from app.repositories.trade_repository import TradeRepository
from app.schemas.position import PositionCreate


class PositionService:

    def __init__(self, position_repo: PositionRepository, trade_repo : TradeRepository, redis : RedisClient):
        self.position_repo = position_repo
        self.trade_repo = trade_repo
        self.redis = redis

    async def get_positions(
            self,
            user_id : UUID,
            status: Optional[PositionStatus] = None
    ) -> list[Position]:
        return list(await self.position_repo.get_user_positions(user_id=user_id, status=status))

    async def get_position(self, user_id : UUID, position_id : UUID) -> Position:
        position = await self.position_repo.get_user_position(user_id=user_id, position_id=position_id)
        if position is None:
            raise NotFoundException("Position")
        return position

    async def open_position(self, user_id:UUID, data:PositionCreate) -> Position:
        existing = await self.position_repo.get_open_position_by_symbol(
            user_id=user_id,
            symbol=data.symbol
        )

        if existing:
            raise BadRequestException(f"Open position for {data.symbol} already exists")
        
        position = await self.position_repo.create_position(
            user_id=user_id,
            symbol=data.symbol,
            quantity=float(data.quantity),
            entry_price=float(data.entry_price),
            position_type=PositionType(data.position_type.value)
        )

        trade_side = TradeSide.BUY if data.position_type.value == "LONG" else TradeSide.SELL
        await self.trade_repo.create_trade(
            user_id=user_id,
            symbol=data.symbol,
            side=trade_side,
            quantity=float(data.quantity),
            price=float(data.entry_price),
            position_id=position.id
        )

        await self.redis.subscribe_user_to_symbol(str(user_id), data.symbol)
        await self.redis.invalidate_user_pnl(str(user_id))

        return position

    async def close_position(
            self,
            user_id : UUID,
            position_id : UUID,
            exit_price : Optional[Decimal] = None
    ) -> Position:
        position = await self.get_position(user_id, position_id)

        if position.status == PositionStatus.CLOSED:
            raise BadRequestException("Position already closed")

        if exit_price is None:
            price = await self.redis.get_price(position.symbol)
            if not price:
                raise BadRequestException("Cannot determine exit price")
            exit_price = Decimal(str(price))
        
        realized_pnl = position.calculate_unrealized_pnl(float(exit_price))

        closed_position = await self.position_repo.close_position(
            position_id=position_id,
            exit_price=float(exit_price),
            realized_pnl=realized_pnl
        )

        trade_side = TradeSide.SELL if position.position_type == PositionType.LONG else TradeSide.BUY

        await self.trade_repo.create_trade(
            user_id=user_id,
            symbol=position.symbol,
            side=trade_side,
            quantity=float(position.quantity),
            price=float(exit_price),
            position_id=position_id,
            realized_pnl=realized_pnl
        )

        remaining = await self.position_repo.get_open_position_by_symbol(
            user_id=user_id, symbol=position.symbol
        )
        if not remaining:
            await self.redis.unsubscribe_user_from_symbol(str(user_id), position.symbol)
        
        await self.redis.invalidate_user_pnl(str(user_id))

        return closed_position
        
        
        