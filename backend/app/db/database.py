from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    async_sessionmaker,
    create_async_engine
)
from app.core.config import settings
from app.models.base import Base

class Database:
    def __init__(self):
        self.engine : AsyncEngine = create_async_engine(
            settings.DATABASE_URL,
            pool_size = settings.DB_POOL_SIZE,
            max_overflow = settings.DB_MAX_OVERFLOW,
            pool_recycle = settings.DB_POOL_RECYCLE,
            pool_pre_ping = True,
            echo = settings.DEBUG
        )

        self.session_factory : async_sessionmaker = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False
        )

    async def create_tables(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def close(self):
        await self.engine.dispose()

db = Database()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with db.session_factory() as session:
        try:
            yield session
            await session.commit()
        except:
            await session.rollback()
            raise
        finally:
            await session.close()

# # ========================= Another way =========================

# class PostgresConnection:
#     '''Manages PostgreSQL async connection'''

#     def __init__(self):
#         self.engine : AsyncEngine | None = None
#         self.session_maker : async_sessionmaker | None = None

#     async def connect(self):
#         '''Initialize db connection'''
#         self.engine = create_async_engine(
#             settings.DATABASE_URL,
#             pool_size = settings.DB_POOL_SIZE,
#             max_overflow = settings.DB_MAX_OVERFLOW,
#             pool_recycle = settings.DB_POOL_RECYCLE,
#             pool_pre_ping = True,
#             echo = settings.DEBUG
#         )

#         self.session_maker = async_sessionmaker(
#             bind=self.engine,
#             class_=AsyncSession,
#             expire_on_commit=False,
#             autocommit = False,
#             autoflush=False
#         )

#         print("PostgreSQL connected")

#     async def disconnect(self):
#         '''close database connection'''
#         if self.engine:
#             await self.engine.dispose()
#             print('PostgreSQL disconnected')

#     async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
#         '''Get database sessions.'''
#         if self.session_maker:
#             async with self.session_maker() as session:
#                 try:
#                     yield session
#                     await session.commit()
#                 except Exception:
#                     await session.rollback()
#                     raise
#         else:
#             raise Exception("db not connected")

# # Global instance
# db_connection = PostgresConnection()

# # Convenience accessors
# async def get_engine() -> AsyncEngine:
#     if db_connection.engine:
#         return db_connection.engine
#     else:
#         raise Exception("db not connected")

# def get_async_session_maker():
#     return db_connection.session_maker

# # Alias for convenience
# async_session_maker = get_async_session_maker

# # for use as a dependency
# async def get_db() -> AsyncGenerator[AsyncSession, None]:
#     async for session in db_connection.get_session():
#         yield session