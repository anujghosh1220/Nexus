from fastapi import Request, HTTPException, status
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from typing import Callable
from app.core.config import settings


def get_identifier(request: Request) -> str:
    """
    Get a unique identifier for rate limiting.
    Uses user ID if authenticated, otherwise IP address.
    """
    # Try to get user ID from request state (set by auth middleware)
    if hasattr(request.state, "user_id") and request.state.user_id:
        return f"user:{request.state.user_id}"
    return get_remote_address(request)


# Create rate limiter
limiter = Limiter(
    key_func=get_identifier,
    default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"],
    storage_uri=settings.REDIS_URL,
)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Custom handler for rate limit exceeded."""
    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail={
            "error": {
                "code": "RATE_LIMIT_EXCEEDED",
                "message": "Rate limit exceeded. Please try again later.",
                "retry_after": str(exc.retry_after) if hasattr(exc, "retry_after") else None
            }
        }
    )
