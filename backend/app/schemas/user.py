
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserResponse(BaseModel):
    '''user response schema'''

    id : UUID
    email : EmailStr
    username : str
    is_active : bool
    is_verified : bool
    created_at : datetime

    class Config:
        from_attributes = True

#  ============= Extras ======================

class UserUpdate(BaseModel):
    '''user update schema'''

    username : Optional[str] = None
    email : Optional[str] = None


class ChangePasswordRequest(BaseModel):
    '''changes password request'''

    current_password : str
    new_password : str
    