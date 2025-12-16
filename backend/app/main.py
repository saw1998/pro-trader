from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.auth.jwt.auth_backend import auth_backend
from app.auth.jwt.auth_user import auth_users
from app.schema.user_schema import UserCreate, UserRead, UserUpdate
from app.db.base_db import Base, db_async_engine

@asynccontextmanager
async def lifespan(app : FastAPI):
    # initialization of stuff
    async with db_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

    await db_async_engine.dispose()


app = FastAPI(lifespan=lifespan)

# Routers

# registration
app.include_router(
    auth_users.get_register_router(user_schema=UserRead, user_create_schema=UserCreate),
    tags=["auth"]
)

#user routes
app.include_router(
    auth_users.get_users_router(user_schema=UserRead, user_update_schema=UserUpdate),
    tags=["users"]
)

# authentication router
app.include_router(
    auth_users.get_auth_router(backend=auth_backend),
    tags=["authentication"]
)
