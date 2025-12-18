from fastapi import HTTPException, status
from typing import Any, Dict, Optional


class AppException(HTTPException):
    def __init__(self, status_code : int, details : str, headers: Optional[dict[str, Any]] = None):
        super().__init__(status_code=status_code, detail=details, headers=headers)

class NotFoundException(AppException):
    def __init__(self, resource: str = "Resource"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, details=f"{resource} not found")

class UnauthorizedException(AppException):
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, details=detail)

class BadRequestException(AppException):
    def __init__(self, detail: str = "Bad Request"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, details=detail)

class ConflictException(AppException):
    def __init__(self, detail: str = "Conflict"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, details=detail)


# ================================= Additional exception ===============================================
class BaseAppException(Exception):
    '''Base exception for application'''

    def __init__(
            self,
            message: str,
            status_code: int = 500,
            details : Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

    
class AuthenticationError(BaseAppException):
    '''Raise when authentication fails'''

    def __init__(self, message: str = "Permission denied"):
        super().__init__(message=message, status_code=status.HTTP_401_UNAUTHORIZED)

class NotFoundError(BaseAppException):
    '''Raise when resource not found'''

    def __init__(self, resource: str, identifier: Any):
        super().__init__(
            message=f"{resource} not found",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"resource" : resource, "identifier" : str(identifier)}
        )

class ValidationError(BaseAppException):
    '''Raise when validation fails'''

    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )

class ConflictError(BaseAppException):
    '''Raise when resource conflict occurs.'''

    def __init__(self, message: str):
        super().__init__(message=message, status_code=status.HTTP_409_CONFLICT)

class RateLimitError(BaseAppException):
    '''Raised when rate limit exceeded'''

    def __init__(self, retry_after: int = 60):
        super().__init__(
            message="Rate limit exceeded",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details={"retry_after" : retry_after}
        )
        