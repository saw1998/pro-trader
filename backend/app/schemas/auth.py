
import re
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    '''User registration request'''

    email: EmailStr
    username : str = Field(..., min_length=3, max_length=50)
    password : str = Field(..., min_length=8, max_length=100)

    @field_validator("username")
    def validate_username(cls, v):
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("Username can only contain letters, numbers and underscore")
        return v.lower()

    @field_validator("password")
    def validate_password(cls, v):
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contains at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contains at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contains at least one digit")
        return v


class LoginRequest(BaseModel):
    '''User login request'''

    email : EmailStr
    password : str

class AuthResponse(BaseModel):
    '''Authentication response'''

    session_id : str
    user_id : str
    username : str
    email : str
    expires_in : int #seconds

class CurrentUser(BaseModel):
    '''Current authenticated user'''

    user_id : str
    email : Optional[str] = None
    username: Optional[str] = None
    session_id : str

class LogoutResponse(BaseModel):
    '''Logout response'''

    message: str = "Successfully logged out"
