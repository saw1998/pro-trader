from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine

import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://localhost:5432/pro_trader")

db_async_engine = create_async_engine(DATABASE_URL, echo=True)
async_db_session_local = async_sessionmaker(db_async_engine, autoflush=False, expire_on_commit=False, class_=AsyncSession)


async def get_async_db_session():
    async with async_db_session_local() as db_session:
        try:
            yield db_session
        except:
            await db_session.rollback()
        finally:
            await db_session.aclose()


class Base(DeclarativeBase):
    pass

