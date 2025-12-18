
from uuid import UUID
from app.core.exceptions import ConflictException, UnauthorizedException
from app.core.security import SecurityService
from app.db.redis import RedisClient
from app.repositories import UserRepository
from app.schemas.auth import LoginResponse


class AuthService:
    def __init__(self, user_repo: UserRepository, redis : RedisClient):
        self.user_repo = user_repo
        self.redis = redis
    
    async def register(self, email: str, username: str, password: str) -> UUID:
        if await self.user_repo.email_exists(email):
            raise ConflictException("Email already exist")
        
        if await self.user_repo.username_exists(username):
            raise ConflictException("Username already exist")
        
        password_hash = SecurityService.hash_password(password)
        user = await self.user_repo.create_user(email, username, password_hash)
        return user.id
    
    async def login(self, email: str, password: str) -> LoginResponse:
        user = await self.user_repo.get_by_email(email)

        if not user or not SecurityService.verify_password(password, user.password_hash):
            raise UnauthorizedException("Invalid email or password")

        if not user.is_active:
            raise UnauthorizedException("Account is deactivated")

        session_id = SecurityService.generate_session_id()
        session_data = {
            "user_id" : str(user.id),
            "username" : user.username,
            "email" : user.email
        }
        await self.redis.create_session(session_id=session_id, user_data = session_data)

        return LoginResponse(
            session_id=session_id,
            user_id=str(user.id),
            username=user.username
        )
    
    async def logout(self, session_id: str) -> None:
        await self.redis.delete_session(session_id)

    async def logout_all(self, user_id: str) -> None:
        await self.redis.delete_user_sessions(user_id)
        