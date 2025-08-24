"""
Middleware для безопасности и логирования
"""

import time
import uuid
from typing import Callable
from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import settings
from app.core.logging import logger
from app.core.security import check_rate_limit, validate_cors_origin


class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware для безопасности"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Проверка trusted hosts
        if settings.environment != "development":
            host = request.headers.get("host", "")
            # Убираем порт из host для проверки
            host_without_port = host.split(":")[0] if ":" in host else host
            
            # Проверяем точное совпадение или wildcard
            allowed = False
            for allowed_host in settings.allowed_hosts:
                if allowed_host == "*":
                    allowed = True
                    break
                elif allowed_host.startswith("*."):
                    # Проверяем wildcard домен
                    domain = allowed_host[2:]  # Убираем "*."
                    if host_without_port.endswith(domain):
                        allowed = True
                        break
                elif allowed_host == host_without_port:
                    allowed = True
                    break
            
            if not allowed:
                return JSONResponse(
                    status_code=403,
                    content={"detail": "Host not allowed"}
                )

        # Проверка rate limit для API endpoints
        if request.url.path.startswith("/api/"):
            try:
                await check_rate_limit(request)
            except Exception as e:
                return JSONResponse(
                    status_code=429,
                    content={"detail": str(e)}
                )

        # Добавление security headers
        response = await call_next(request)
        
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        if settings.environment == "production":
            response.headers["Content-Security-Policy"] = "default-src 'self'"

        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware для логирования запросов"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Генерируем уникальный ID для запроса
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Проверяем, является ли это health check
        is_health_check = request.url.path == "/health"
        
        # Логируем начало запроса (только для не-health check запросов)
        start_time = time.time()
        
        # Всегда логируем детали запроса для отладки
        logger.info(
            f"Request details",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "path": request.url.path,
                "client_ip": request.client.host if request.client else "unknown",
                "user_agent": request.headers.get("user-agent", ""),
                "is_health_check": is_health_check
            }
        )
        
        if not is_health_check:
            logger.info(
                f"Request started",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "url": str(request.url),
                    "client_ip": request.client.host if request.client else "unknown",
                    "user_agent": request.headers.get("user-agent", "")
                }
            )

        try:
            response = await call_next(request)
            
            # Логируем ответ (только для не-health check запросов или при ошибках)
            process_time = time.time() - start_time
            
            if not is_health_check or response.status_code >= 400:
                logger.info(
                    f"Request completed",
                    extra={
                        "request_id": request_id,
                        "status_code": response.status_code,
                        "process_time": process_time
                    }
                )
            
            # Добавляем request ID в заголовки
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            # Логируем ошибку (всегда, включая health checks)
            process_time = time.time() - start_time
            logger.error(
                f"Request failed: {str(e)}",
                extra={
                    "request_id": request_id,
                    "error": str(e),
                    "process_time": process_time,
                    "is_health_check": is_health_check
                }
            )
            raise


class IdempotencyMiddleware(BaseHTTPMiddleware):
    """Middleware для идемпотентности запросов"""

    def __init__(self, app, cache=None):
        super().__init__(app)
        self.cache = cache or {}  # В реальном проекте используется Redis

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Проверяем только для POST/PUT/PATCH запросов
        if request.method in ["POST", "PUT", "PATCH"]:
            idempotency_key = request.headers.get("Idempotency-Key")
            
            if idempotency_key:
                # Проверяем, был ли уже обработан запрос с таким ключом
                if idempotency_key in self.cache:
                    cached_response = self.cache[idempotency_key]
                    return JSONResponse(
                        status_code=cached_response["status_code"],
                        content=cached_response["content"],
                        headers=cached_response["headers"]
                    )
                
                # Обрабатываем запрос
                response = await call_next(request)
                
                # Кэшируем ответ
                self.cache[idempotency_key] = {
                    "status_code": response.status_code,
                    "content": response.body.decode() if hasattr(response, 'body') else "",
                    "headers": dict(response.headers)
                }
                
                return response
        
        return await call_next(request)


class WebhookSignatureMiddleware(BaseHTTPMiddleware):
    """Middleware для проверки подписи webhook"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Проверяем только для webhook endpoints
        if request.url.path.startswith("/api/webhooks/"):
            signature = request.headers.get("X-Webhook-Signature")
            
            if not signature:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Missing webhook signature"}
                )
            
            # Читаем тело запроса
            body = await request.body()
            
            # Проверяем подпись
            from app.core.security import SecurityUtils
            if not SecurityUtils.verify_webhook_signature(
                body.decode(),
                signature,
                settings.amocrm_webhook_secret
            ):
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Invalid webhook signature"}
                )
        
        return await call_next(request)


def setup_middleware(app):
    """Настройка всех middleware"""
    
    # Trusted Host Middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.allowed_hosts
    )
    
    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["*"],
    )
    
    # Security Middleware
    app.add_middleware(SecurityMiddleware)
    
    # Logging Middleware
    app.add_middleware(LoggingMiddleware)
    
    # Idempotency Middleware
    app.add_middleware(IdempotencyMiddleware)
    
    # Webhook Signature Middleware
    app.add_middleware(WebhookSignatureMiddleware)
