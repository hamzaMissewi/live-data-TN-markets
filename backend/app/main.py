"""FastAPI main application."""

import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.api.v1 import api_v1_router
from app.db.session import init_db, close_db
from app.utils.logger import setup_logger

# Import all models to register them with Base.metadata
import app.models  # noqa: F401

logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")

    # Initialize database
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")

    yield

    # Shutdown
    logger.info("Shutting down...")
    await close_db()
    logger.info("Application stopped")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Tunisia Markets Hub API - Stock prices, FX rates, anomalies, and more",
    lifespan=lifespan,
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    openapi_url="/openapi.json" if settings.ENVIRONMENT != "production" else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*.tunisia-markets.com", "localhost", "127.0.0.1"],
    )


class LoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        logger.info(
            f"{request.method} {request.url.path} "
            f"-> {response.status_code} in {process_time:.4f}s"
        )

        response.headers["X-Process-Time"] = f"{process_time:.4f}"
        response.headers["X-API-Version"] = settings.APP_VERSION

        return response


app.add_middleware(LoggingMiddleware)

# Include API routes
app.include_router(api_v1_router, prefix=settings.API_PREFIX)


# Health check
@app.get("/health")
async def health():
    """Simple health check."""
    return {"status": "ok", "version": settings.APP_VERSION}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "Tunisia Markets Hub API",
        "docs": "/docs" if settings.ENVIRONMENT != "production" else "disabled",
        "api": settings.API_PREFIX,
    }


# Mount static files
try:
    app.mount("/static", StaticFiles(directory="backend/static"), name="static")
except Exception:
    pass


# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    from fastapi.openapi.utils import get_openapi

    openapi_schema = get_openapi(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Tunisia Markets Hub API",
        routes=app.routes,
    )

    openapi_schema["info"]["contact"] = {
        "name": "Tunisia Markets Hub",
        "email": "contact@tunisia-markets.com",
        "url": "https://tunisia-markets.com",
    }

    openapi_schema["info"]["license"] = {
        "name": "MIT",
        "url": "https://opensource.org/license/mit/",
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Custom 404 handler."""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "The requested resource was not found",
            "path": request.url.path,
        },
    )


@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    """Custom 500 handler."""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "path": request.url.path,
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
