from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.positions import Position, PositionStatus
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
    
    async 