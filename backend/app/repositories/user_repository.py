from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    '''Repository for users operations'''

    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_email(self, email:str) -> Optional[User]:
        '''get user by email'''
        query = select(User).where(User.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_username(self, username : str) -> Optional[User]:
        query = select(User).where(User.username == username)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def email_exists(self, email: str) -> bool:
        user = await self.get_by_email(email)
        return user is not None

    async def username_exists(self, username : str) -> bool:
        user = await self.get_by_username(username)
        return user is not None

    async def create_user(self, email: str, username : str, password_hash : str) -> User:
        user = User(email=email, username = username, password_hash = password_hash)
        return await self.create(user)

    async def update_password(self, user_id : UUID, password_hash : str) -> bool:
        user = await self.get_by_id(user_id)
        if user:
            user.password_hash = password_hash
            await self.update(user)
            return True
        return False

    async def deactivate(self, user_id : UUID) -> bool:
        '''Deactivate user account'''
        user = await self.get_by_id(user_id)
        if user:
            user.is_active = False
            await self.update(user)
            return True
        return False
        