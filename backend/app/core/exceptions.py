from typing import Any, Optional
from fastapi import HTTPException, status


class NEXUSException(Exception):
    """Base exception for NEXUS application."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        code: str = "INTERNAL_ERROR",
        details: Optional[dict] = None
    ):
        self.message = message
        self.status_code = status_code
        self.code = code
        self.details = details or {}
        super().__init__(message)


class AuthenticationError(NEXUSException):
    """Authentication failed."""

    def __init__(self, message: str = "Authentication failed", details: Optional[dict] = None, status_code: int = status.HTTP_401_UNAUTHORIZED):
        super().__init__(
            message=message,
            status_code=status_code,
            code="AUTHENTICATION_ERROR",
            details=details
        )


class AuthorizationError(NEXUSException):
    """Authorization failed - insufficient permissions."""

    def __init__(self, message: str = "You don't have permission to perform this action", details: Optional[dict] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            code="AUTHORIZATION_ERROR",
            details=details
        )


class ResourceNotFoundError(NEXUSException):
    """Resource not found."""

    def __init__(self, resource: str = "Resource", details: Optional[dict] = None):
        super().__init__(
            message=f"{resource} not found",
            status_code=status.HTTP_404_NOT_FOUND,
            code="RESOURCE_NOT_FOUND",
            details=details
        )


class ValidationError(NEXUSException):
    """Validation error."""

    def __init__(self, message: str = "Validation failed", details: Optional[dict] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="VALIDATION_ERROR",
            details=details
        )


class ConflictError(NEXUSException):
    """Resource conflict - duplicate or inconsistent state."""

    def __init__(self, message: str = "Resource conflict", details: Optional[dict] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            code="CONFLICT_ERROR",
            details=details
        )


class RateLimitError(NEXUSException):
    """Rate limit exceeded."""

    def __init__(self, message: str = "Rate limit exceeded", details: Optional[dict] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            code="RATE_LIMIT_ERROR",
            details=details
        )


class TenantIsolationError(NEXUSException):
    """Attempted cross-tenant access."""

    def __init__(self, message: str = "Access denied - tenant isolation violation", details: Optional[dict] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            code="TENANT_ISOLATION_ERROR",
            details=details
        )
