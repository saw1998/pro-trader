
from typing import Generic, List, Optional, Type, TypeVar
from uuid import UUID

from sqlalchemy import delete, select
from app.models.base import Base
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    '''Base repository with common crud operations'''
    
    def __init__(self, model: Type[ModelType], session : AsyncSession):
        self.model = model
        self.session = session

    async def get_by_id(self, id:UUID) -> Optional[ModelType]:
        '''get entity by ID'''
        query = select(self.model).where(self.model.id == id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_all(self, skip:int = 0, limit:int=0) -> List[ModelType]:
        query = select(self.model).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create(self, entity : ModelType) -> ModelType:
        '''create new entity'''
        self.session.add(entity)
        await self.session.flush() # below is the documentation on why
        await self.session.refresh(entity)
        return entity
    
    '''
    await self.session.flush()
    flush() sends all pending changes (like add) to the database without committing.

    Why? Because:

    You may need auto-generated fields (like id from a primary key or defaults) to be populated.

    You can continue adding more objects before committing as a batch.

    Important:

    flush() does not commit the transaction, so the changes can still be rolled back.

    In async SQLAlchemy, you must await it.

    4️⃣ Refresh the entity
    python
    Copy code
    await self.session.refresh(entity)
    refresh() reloads the entity from the database.

    Why? To make sure:

    Any server-generated defaults (like timestamps, sequences, triggers) are populated on the Python object.

    After this, entity contains the final state from the DB.
    '''

    async def update(self, entity: ModelType) -> ModelType:
        '''update entity'''
        await self.session.flush()
        await self.session.refresh(entity)
        return entity
    '''
    Example:

    user.username = "new_username"
    await user_repo.update(user)


    flush() ensures new_username is written to the database.
    '''

    async def delete(self, entity : ModelType) -> bool:
        '''delete entity'''
        await self.session.delete(entity)
        await self.session.flush()
        return True
    
    async def delete_by_id(self, id: UUID) -> bool:
        query = delete(self.model).where(self.model.id == id)
        result = await self.session.execute(query)
        return result.rowcount > 0
        