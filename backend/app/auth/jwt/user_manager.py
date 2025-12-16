from fastapi import Depends
from fastapi_users import BaseUserManager, UUIDIDMixin
from app.db.base_db import get_async_db_session
from app.models.user_model import User
from dotenv import load_dotenv
import os
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

SECRET = os.getenv("JWT_SECRET", "dev-secret-key")


class UserManager(UUIDIDMixin, BaseUserManager[User, str]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET


async def get_user_db(db_session: AsyncSession = Depends(get_async_db_session)):
    yield SQLAlchemyUserDatabase(db_session, User)

async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)