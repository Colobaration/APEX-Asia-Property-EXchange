from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import os
from datetime import datetime
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.exceptions import APEXException, ValidationError, DatabaseError, ExternalServiceError
from app.core.middleware import setup_middleware

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
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "authentication",
            "description": "Операции с аутентификацией и авторизацией"
        },
        {
            "name": "leads",
            "description": "Управление лидами и сделками"
        },
        {
            "name": "analytics",
            "description": "Аналитика и отчеты"
        },
        {
            "name": "notifications",
            "description": "Система уведомлений"
        },
        {
            "name": "webhooks",
            "description": "Webhook обработчики"
        }
    ]
)

# Настройка middleware
setup_middleware(app)

# Обработчики исключений
@app.exception_handler(APEXException)
async def apex_exception_handler(request: Request, exc: APEXException):
    """Обработчик для APEX исключений"""
    logger.error(f"APEX Exception: {exc.message}", extra={
        "status_code": exc.status_code,
        "details": exc.details,
        "path": request.url.path
    })
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.message,
                "type": exc.__class__.__name__,
                "details": exc.details
            }
        }
    )


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """Обработчик для ошибок валидации"""
    logger.warning(f"Validation Error: {exc.message}", extra={
        "details": exc.details,
        "path": request.url.path
    })
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.message,
                "type": "ValidationError",
                "details": exc.details
            }
        }
    )


@app.exception_handler(DatabaseError)
async def database_exception_handler(request: Request, exc: DatabaseError):
    """Обработчик для ошибок базы данных"""
    logger.error(f"Database Error: {exc.message}", extra={
        "path": request.url.path
    })
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": "Внутренняя ошибка сервера",
                "type": "DatabaseError"
            }
        }
    )


@app.exception_handler(ExternalServiceError)
async def external_service_exception_handler(request: Request, exc: ExternalServiceError):
    """Обработчик для ошибок внешних сервисов"""
    logger.error(f"External Service Error: {exc.message}", extra={
        "service": exc.details.get("service"),
        "path": request.url.path
    })
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.message,
                "type": "ExternalServiceError",
                "details": exc.details
            }
        }
    )


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint для Kubernetes probes и мониторинга"""
    return {
        "status": "healthy",
        "environment": settings.environment,
        "version": "1.0.0",
        "debug": settings.debug,
        "timestamp": datetime.utcnow().isoformat()
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
