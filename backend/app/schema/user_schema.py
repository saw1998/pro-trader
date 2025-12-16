from fastapi_users import schemas
from uuid import UUID

class UserRead(schemas.BaseUser[UUID]):
    pass
    # role: str

class UserCreate(schemas.BaseUserCreate):
    pass
    # role: str = "user"

class UserUpdate(schemas.BaseUserUpdate):
    pass
    # role: str | None = None