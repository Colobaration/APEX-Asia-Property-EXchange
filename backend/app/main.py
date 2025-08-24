from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import logging
import os
from app.core.config import settings
from app.core.logging import setup_logging

# Настройка логирования
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Startup
    logger.info(f"Starting APEX API in {settings.environment} environment")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Log level: {settings.log_level}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down APEX API")

app = FastAPI(
    title="APEX Asia Property Exchange API",
    description="API для системы управления недвижимостью в Азии",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)

# Trusted Host middleware
if not settings.debug:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.allowed_hosts
    )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint для Kubernetes probes и мониторинга"""
    return {
        "status": "healthy",
        "environment": settings.environment,
        "version": "1.0.0",
        "debug": settings.debug
    }

@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "message": "APEX Asia Property Exchange API",
        "version": "1.0.0",
        "environment": settings.environment,
        "docs": "/docs" if settings.debug else "disabled in production"
    }

# Подключаем все API роутеры
try:
    from app.api import webhooks, auth, leads, analytics, notifications
    
    # Webhooks роутер
    app.include_router(
        webhooks.router, 
        prefix=f"{settings.api_prefix}/webhooks", 
        tags=["webhooks"]
    )
    
    # Auth роутер
    app.include_router(
        auth.router, 
        prefix=f"{settings.api_prefix}/auth", 
        tags=["authentication"]
    )
    
    # Leads роутер
    app.include_router(
        leads.router, 
        prefix=f"{settings.api_prefix}/leads", 
        tags=["leads"]
    )
    
    # Analytics роутер
    app.include_router(
        analytics.router, 
        prefix=f"{settings.api_prefix}/analytics", 
        tags=["analytics"]
    )
    
    # Notifications роутер
    app.include_router(
        notifications.router, 
        prefix=f"{settings.api_prefix}/notifications", 
        tags=["notifications"]
    )
    
    logger.info("All API routers loaded successfully")
    
except ImportError as e:
    logger.warning(f"Some API modules not available: {e}")

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Endpoint not found", "path": request.url.path}

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return {"error": "Internal server error"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
