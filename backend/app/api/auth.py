

from typing import Optional
from fastapi import APIRouter, Depends, Header, status

from app.db.redis import RedisClient, get_redis
from app.dependencies import get_current_user_id, get_user_repo
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, LoginResponse, RegisterRequest
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService


router = APIRouter(prefix="/auth", tags=["auth"])

async def get_auth_service(
        user_repo : UserRepository = Depends(get_user_repo),
        redis : RedisClient = Depends(get_redis)
) -> AuthService :
    return AuthService(user_repo, redis)

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    data: RegisterRequest,
    service : AuthService = Depends(get_auth_service)
):
    user_id = await service.register(data.email, data.username, data.password)
    return {
        "user_id" : str(user_id),
        "message" : "Registration Successfull"
    }

@router.post("/login", response_model=LoginResponse)
async def login(
    data : LoginRequest,
    service : AuthService = Depends(get_auth_service)
):
    return await service.login(data.email, data.password)

@router.post("/logout")
async def logout(
    authorization : Optional[str] = Header(None),
    service: AuthService = Depends(get_auth_service)
):
    if authorization:
        try:
            _, session_id = authorization.split(" ", 1)
            await service.logout(session_id)
        except ValueError:
            pass
    return {
        "message" : "Logged out"
    }

@router.get('/me', response_model=UserResponse)
async def get_me(
    user_id = Depends(get_current_user_id),
    user_repo : UserRepository = Depends(get_user_repo)
):
    user = await user_repo.get_by_id(user_id)
    return user
