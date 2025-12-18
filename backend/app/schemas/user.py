
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    '''base user schema'''
    
    email : EmailStr
    username : str

class UserResponse(UserBase):
    '''user response schema'''

    id : UUID
    is_active : bool
    is_verified : bool
    created_at : datetime

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    '''user update schema'''

    username : Optional[str] = None
    email : Optional[str] = None


class ChangePasswordRequest(BaseModel):
    '''changes password request'''

    current_password : str
    new_password : str
    