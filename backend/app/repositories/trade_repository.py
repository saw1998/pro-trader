from typing import Optional
from uuid import UUID
from sqlalchemy import Sequence, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.trade import Trade, TradeSide
from app.repositories.base import BaseRepository


class TradeRepository(BaseRepository[Trade]):
    def __init__(self, session: AsyncSession):
        super().__init__(Trade, session)

    async def get_user_trades(
            self,
            user_id: UUID,
            skip : int = 0,
            limit : int = 50
    ) -> list[Trade]:
        result = await self.session.execute(
            select(Trade)
            .where(Trade.user_id == user_id)
            .order_by(Trade.executed_at.desc())
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_position_trades(self, position_id: UUID) -> list[Trade]:
        result = await self.session.execute(
            select(Trade)
            .where(Trade.position_id == position_id)
            .order_by(Trade.executed_at.desc())
        )
        return list(result.scalars().all())
    
    async def create_trade(
        self,
        user_id: UUID,
        symbol: str,
        side: TradeSide,
        quantity: float,
        price: float,
        position_id: Optional[UUID] = None,
        fee: float = 0,
        realized_pnl: float = 0
    ) -> Trade:
        trade = Trade(
            user_id=user_id,
            position_id=position_id,
            symbol=symbol.upper(),
            side=side,
            quantity=quantity,
            price=price,
            total_value=quantity * price,
            fee=fee,
            realized_pnl=realized_pnl
        )
        return await self.create(trade)
