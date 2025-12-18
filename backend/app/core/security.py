import secrets
from passlib.context import CryptContext
from app.config import settings

# Password hashing
pwd_context = CryptContext(schemes=['bcrypt'], depricated="auto", bcrypt__rounds=settings.BCRYPT_ROUNDS)

def hash_password(password : str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hash=hashed_password)

def generate_session_id() -> str:
    '''Generate a cryptographically secure session ID'''
    return secrets.token_urlsafe(32)

# class SessionManager:
#     '''Manages user sessions in Redis.'''

#     SESSION_PREFIX = "session:"
#     USER_SESSION_PREFIX = "user_sessions:"

#     def __init__(self):
#         self.redis = redis_client