from datetime import datetime
from typing import List, Optional
from uuid import UUID
from zoneinfo import ZoneInfo
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.positions import Position, PositionStatus, PositionType
from app.repositories.base import BaseRepository


class PositionRepository(BaseRepository[Position]):
    '''repository for position operations'''

    def __init__(self, session : AsyncSession):
        super().__init__(model=Position,session=session)

    async def get_user_positions(
            self, 
            user_id : UUID, 
            status: Optional[PositionStatus] = None,
            skip : int = 0,
            limit: int = 100
        ) -> List[Position]:
        '''Get all positions for a user'''
        query = select(Position).where(Position.user_id == user_id)

        if status:
            query = query.where(Position.status == status)

        query = query.order_by(Position.created_at.desc())
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_user_open_positions(self, user_id : UUID) -> list[Position]:
        return await self.get_user_positions(user_id=user_id, status=PositionStatus.OPEN)

    async def get_user_position(self, user_id : UUID, position_id : UUID) -> Optional[Position]:
        result = await self.session.execute(
            select(Position).where(and_(Position.id == position_id, Position.user_id == user_id))
        )
        return result.scalar_one_or_none()

    async def get_open_position_by_symbol(self, user_id:UUID, symbol:str) -> Optional[Position]:
        result = await self.session.execute(
            select(Position).where(
                and_(
                    Position.user_id == user_id,
                    Position.symbol == symbol,
                    Position.status == PositionStatus.OPEN
                )
            )
        )
        return result.scalar_one_or_none()

    async def create_position(self, user_id:UUID, symbol:str, quantity:float, entry_price : float, position_type: PositionType) -> Position:
        position = Position(
            user_id=user_id,
            symbol = symbol,
            quantity = quantity,
            entry_price = entry_price,
            position_type = position_type,
            status = PositionStatus.OPEN
        )
        return await self.create(position)

    async def close_position(self, position_id: UUID, exit_price: float, realized_pnl: float) -> Optional[Position]:
        """
        Close an open position by updating its status and recording exit details.
        
        This method updates an existing position record with closing information:
        - Sets status to CLOSED
        - Records the exit price
        - Calculates and stores realized P&L
        - Timestamps the closing event
        
        Args:
            position_id: Unique identifier of the position to close
            exit_price: Price at which the position was closed
            realized_pnl: Calculated profit or loss from the position
            
        Returns:
            Updated Position object if found, None if position doesn't exist
            
        Note: This method fetches the existing position first, then updates it
        rather than creating a new Position object (which would cause issues)
        """
        # FIXED: Fetch existing position first, then update its fields
        position = await self.get_by_id(position_id)
        if not position:
            return None
            
        # Update the position fields for closing
        position.status = PositionStatus.CLOSED
        position.exit_price = exit_price
        position.realized_pnl = realized_pnl
        position.closed_at = datetime.now(tz=ZoneInfo("UTC"))
        
        # Save the updated position
        return await self.update(position)
    
    async def get_positions_by_symbol(self, symbol: str) -> list[Position]:
        result = await self.session.execute(
            select(Position).where(
                and_(
                    Position.symbol == symbol.upper(),
                    Position.status == PositionStatus.OPEN
                )
            )
        )
        return list(result.scalars().all())

    async def get_user_symbols(self, user_id : UUID) -> list[str]:
        result = await self.session.execute(
            select(Position.symbol).where(
                and_(
                    Position.user_id == user_id,
                    Position.status == PositionStatus.OPEN
                )
            ).distinct()
        )
        return [row[0] for row in result.fetchall()]
    



    