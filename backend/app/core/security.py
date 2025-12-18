import secrets
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=['bcrypt'], depricated="auto")


class SecurityService:
    @staticmethod
    def hash_password(password : str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hash=hashed_password)

    @staticmethod
    def generate_session_id() -> str:
        '''Generate a cryptographically secure session ID'''
        return secrets.token_urlsafe(32)