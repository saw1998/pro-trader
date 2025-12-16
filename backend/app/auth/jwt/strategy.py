from fastapi_users.authentication import JWTStrategy
from fastapi_users.jwt import generate_jwt
import os
from dotenv import load_dotenv
from app.models.user_model import User




class RoleJWTStrategy(JWTStrategy):
    async def write_token(self, user: User) -> str:
        data = {"sub": str(user.id), "aud": self.token_audience}
        # data = {"sub" : str(user.id), "aud":self.token_audience, "role" : user.role, "email" : user.email}
        return generate_jwt(
            data, self.encode_key, self.lifetime_seconds, algorithm=self.algorithm
        )


def get_jwt_strategy() -> RoleJWTStrategy:
    return RoleJWTStrategy(
        secret=os.getenv("JWT_SECRET", "SUPER_SECRET_JWT_KEY"),
        lifetime_seconds=3600
    )