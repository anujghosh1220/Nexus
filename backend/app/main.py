from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.logging import logger
from app.core.rate_limit import limiter, rate_limit_exceeded_handler
from app.core.exceptions import NEXUSException
from app.api.v1 import auth, organizations, projects, teams, tasks, two_factor, audit_logs, api_keys, notifications, files


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.APP_NAME,
        description="Production-grade workspace platform for teams, projects, workflows, and APIs.",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Rate limit exception handler
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

    # Custom exception handler
    @app.exception_handler(NEXUSException)
    async def nexus_exception_handler(request, exc: NEXUSException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details
                }
            }
        )

    # Health check endpoints
    @app.get("/health")
    async def health_check():
        """Basic health check - application is alive."""
        return {"status": "healthy", "service": settings.APP_NAME}

    @app.get("/ready")
    async def readiness_check():
        """Readiness check - verifies dependencies."""
        # TODO: Add actual dependency checks (PostgreSQL, Redis)
        return {"status": "ready", "service": settings.APP_NAME}

    # Include routers
    app.include_router(auth.router, prefix=settings.API_V1_PREFIX, tags=["auth"])
    app.include_router(organizations.router, prefix=settings.API_V1_PREFIX, tags=["organizations"])
    app.include_router(projects.router, prefix=settings.API_V1_PREFIX, tags=["projects"])
    app.include_router(teams.router, prefix=settings.API_V1_PREFIX, tags=["teams"])
    app.include_router(tasks.router, prefix=settings.API_V1_PREFIX, tags=["tasks"])
    app.include_router(two_factor.router, prefix=settings.API_V1_PREFIX, tags=["2fa"])
    app.include_router(audit_logs.router, prefix=settings.API_V1_PREFIX, tags=["audit-logs"])
    app.include_router(api_keys.router, prefix=settings.API_V1_PREFIX, tags=["api-keys"])
    app.include_router(notifications.router, prefix=settings.API_V1_PREFIX, tags=["notifications"])
    app.include_router(files.router, prefix=settings.API_V1_PREFIX, tags=["files"])

    logger.info(f"Application {settings.APP_NAME} initialized")

    return app


app = create_application()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
