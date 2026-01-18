"""
Custom exception classes for production-grade error handling
"""
from fastapi import HTTPException, status
from typing import Optional, Any, Dict


class BaseAPIException(HTTPException):
    """Base exception class for API errors"""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code or self.__class__.__name__


class ValidationError(BaseAPIException):
    """Raised when input validation fails"""
    
    def __init__(self, detail: str, error_code: str = "VALIDATION_ERROR"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code=error_code
        )


class NotFoundError(BaseAPIException):
    """Raised when a resource is not found"""
    
    def __init__(self, resource: str, identifier: Any = None, error_code: str = "NOT_FOUND"):
        detail = f"{resource} not found"
        if identifier is not None:
            detail = f"{resource} with id {identifier} not found"
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code=error_code
        )


class ConflictError(BaseAPIException):
    """Raised when a resource conflict occurs (e.g., duplicate entry)"""
    
    def __init__(self, detail: str, error_code: str = "CONFLICT"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code=error_code
        )


class UnauthorizedError(BaseAPIException):
    """Raised when authentication is required or fails"""
    
    def __init__(self, detail: str = "Authentication required", error_code: str = "UNAUTHORIZED"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code=error_code,
            headers={"WWW-Authenticate": "Bearer"}
        )


class ForbiddenError(BaseAPIException):
    """Raised when user lacks permission for the requested action"""
    
    def __init__(self, detail: str = "Insufficient permissions", error_code: str = "FORBIDDEN"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code=error_code
        )


class DatabaseError(BaseAPIException):
    """Raised when a database operation fails"""
    
    def __init__(self, detail: str = "Database operation failed", error_code: str = "DATABASE_ERROR"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code=error_code
        )


class ExternalServiceError(BaseAPIException):
    """Raised when an external service call fails"""
    
    def __init__(self, service: str, detail: str = None, error_code: str = "EXTERNAL_SERVICE_ERROR"):
        detail = detail or f"External service {service} is unavailable"
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            error_code=error_code
        )


class RateLimitError(BaseAPIException):
    """Raised when rate limit is exceeded"""
    
    def __init__(self, retry_after: int = 60, error_code: str = "RATE_LIMIT_EXCEEDED"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
            error_code=error_code,
            headers={"Retry-After": str(retry_after)}
        )
