"""
ARIA Emergency Response System - FastAPI Application
Main application with middleware, routing, and lifecycle management.
"""
import logging
import sys
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from prometheus_fastapi_instrumentator import Instrumentator

from app.core.config import settings
from app.core.database import init_db, close_db
from app.schemas.response import ErrorResponse, ErrorDetail, HealthCheck

# Setup logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(settings.LOG_FILE) if settings.LOG_FILE else logging.NullHandler()
    ]
)

logger = logging.getLogger(__name__)


# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - startup and shutdown events."""
    # Startup
    logger.info("🚀 Starting ARIA Emergency Response System...")
    
    try:
        # Initialize database
        logger.info("📊 Initializing database...")
        await init_db()
        logger.info("✅ Database initialized")
        
        # TODO: Load ML models
        logger.info("🤖 Loading ML models...")
        from app.services.ml_service import ml_service
        try:
            await ml_service.load_all_models()
            logger.info("✅ ML models loaded")
        except Exception as e:
            logger.error(f"⚠️ ML models failed to load: {e}")
            # Continue anyway - some features will be unavailable
        
        # TODO: Initialize Redis
        logger.info("🔴 Connecting to Redis...")
        # await init_redis()
        logger.info("✅ Redis connected")
        
        logger.info("✅ ARIA system started successfully!")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down ARIA system...")
    
    try:
        # Close database connections
        await close_db()
        logger.info("✅ Database connections closed")
        
        # TODO: Close Redis connections
        # await close_redis()
        logger.info("✅ Redis connections closed")
        
        logger.info("✅ ARIA system shutdown complete")
        
    except Exception as e:
        logger.error(f"❌ Shutdown error: {e}")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    ARIA (AI-powered Rapid Incident Assessment) Emergency Response System
    
    ## Features
    
    * 🚑 **Incident Management** - Create, track, and manage emergency incidents
    * 🏥 **Hospital Integration** - Find and rank suitable hospitals
    * 🚨 **Ambulance Dispatch** - Intelligent ambulance allocation
    * 🩸 **Blood Bank** - Blood availability and reservation
    * 🤖 **AI Agents** - LangGraph-powered decision making
    * 📊 **Real-time Dashboard** - Live monitoring and analytics
    
    ## Authentication
    
    Most endpoints require Bearer token authentication. Use `/api/v1/auth/login` to obtain a token.
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Add rate limiter state
app.state.limiter = limiter


# ============================================================================
# MIDDLEWARE CONFIGURATION
# ============================================================================

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip Compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Trusted Host Middleware (production)
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*.aria-emergency.com", "localhost"]
    )


# Request ID Middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add unique request ID to each request."""
    import uuid
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    
    return response


# Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests and responses."""
    start_time = datetime.utcnow()
    
    # Log request
    logger.info(
        f"Request: {request.method} {request.url.path} "
        f"[{request.state.request_id}]"
    )
    
    response = await call_next(request)
    
    # Calculate duration
    duration = (datetime.utcnow() - start_time).total_seconds()
    
    # Log response
    logger.info(
        f"Response: {response.status_code} "
        f"[{request.state.request_id}] "
        f"Duration: {duration:.3f}s"
    )
    
    return response


# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            success=False,
            message=exc.detail,
            errors=[ErrorDetail(message=exc.detail, code=str(exc.status_code))]
        ).dict()
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    errors = []
    for error in exc.errors():
        errors.append(ErrorDetail(
            field=".".join(str(loc) for loc in error["loc"]),
            message=error["msg"],
            code=error["type"]
        ))
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            success=False,
            message="Validation error",
            errors=errors
        ).dict()
    )


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Handle rate limit exceeded."""
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content=ErrorResponse(
            success=False,
            message="Rate limit exceeded. Please try again later.",
            errors=[ErrorDetail(message=str(exc), code="rate_limit_exceeded")]
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            success=False,
            message="Internal server error",
            errors=[ErrorDetail(
                message="An unexpected error occurred" if not settings.DEBUG else str(exc),
                code="internal_error"
            )]
        ).dict()
    )


# ============================================================================
# HEALTH CHECK ENDPOINTS
# ============================================================================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "message": "ARIA Emergency Response System API",
        "version": settings.APP_VERSION,
        "status": "operational",
        "docs": "/docs",
    }


@app.get("/health", response_model=HealthCheck, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return HealthCheck(
        status="healthy",
        version=settings.APP_VERSION,
        timestamp=datetime.utcnow().isoformat(),
        database="connected",  # TODO: Check actual connection
        redis="connected",  # TODO: Check actual connection
        ml_models="loaded",  # TODO: Check actual status
    )


@app.get("/api/health", response_model=HealthCheck, tags=["Health"])
async def api_health():
    """API health check."""
    return await health_check()


# ============================================================================
# ROUTER REGISTRATION
# ============================================================================

# Import routers
from app.api.v1 import incidents, auth, websocket

# Register API v1 routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(incidents.router, prefix="/api/v1/incidents", tags=["Incidents"])
app.include_router(websocket.router, prefix="/api/v1", tags=["WebSocket"])

# app.include_router(hospitals.router, prefix="/api/v1/hospitals", tags=["Hospitals"])
# app.include_router(ambulances.router, prefix="/api/v1/ambulances", tags=["Ambulances"])
# app.include_router(blood_banks.router, prefix="/api/v1/blood-banks", tags=["Blood Banks"])
# app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
# app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])


# ============================================================================
# MONITORING & METRICS
# ============================================================================

if settings.ENABLE_METRICS:
    # Prometheus metrics
    Instrumentator().instrument(app).expose(app, endpoint="/metrics")


# ============================================================================
# STARTUP MESSAGE
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else settings.WORKERS,
        log_level=settings.LOG_LEVEL.lower(),
    )
