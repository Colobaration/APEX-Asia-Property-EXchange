"""
Тесты для модулей безопасности
"""

import pytest
import jwt
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from app.core.security import SecurityUtils, RateLimiter
from app.core.config import settings


class TestSecurityUtils:
    """Тесты для утилит безопасности"""

    def test_verify_password(self):
        """Тест проверки пароля"""
        password = "test_password_123"
        hashed = SecurityUtils.get_password_hash(password)
        
        # Проверяем, что пароль корректно хешируется и проверяется
        assert SecurityUtils.verify_password(password, hashed) is True
        assert SecurityUtils.verify_password("wrong_password", hashed) is False

    def test_create_access_token(self):
        """Тест создания JWT токена"""
        data = {"sub": "123", "email": "test@example.com"}
        token = SecurityUtils.create_access_token(data)
        
        # Проверяем, что токен создается и может быть декодирован
        payload = SecurityUtils.verify_token(token)
        assert payload is not None
        assert payload["sub"] == "123"
        assert payload["email"] == "test@example.com"

    def test_verify_token_invalid(self):
        """Тест проверки недействительного токена"""
        # Недействительный токен
        invalid_token = "invalid.token.here"
        payload = SecurityUtils.verify_token(invalid_token)
        assert payload is None

    def test_verify_token_expired(self):
        """Тест проверки истекшего токена"""
        # Создаем токен с прошлой датой истечения
        data = {"sub": "123", "exp": datetime.utcnow() - timedelta(hours=1)}
        expired_token = jwt.encode(data, settings.jwt_secret, algorithm=settings.jwt_algorithm)
        
        payload = SecurityUtils.verify_token(expired_token)
        assert payload is None

    def test_generate_api_key(self):
        """Тест генерации API ключа"""
        api_key = SecurityUtils.generate_api_key()
        
        # Проверяем, что ключ генерируется и имеет правильную длину
        assert len(api_key) > 0
        assert isinstance(api_key, str)

    def test_hash_api_key(self):
        """Тест хеширования API ключа"""
        api_key = "test_api_key_123"
        hashed = SecurityUtils.hash_api_key(api_key)
        
        # Проверяем, что хеш создается и отличается от оригинала
        assert hashed != api_key
        assert len(hashed) == 64  # SHA256 hash length

    def test_verify_webhook_signature(self):
        """Тест проверки подписи webhook"""
        payload = '{"test": "data"}'
        secret = "test_secret"
        
        # Создаем правильную подпись
        import hmac
        import hashlib
        expected_signature = hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Проверяем правильную подпись
        assert SecurityUtils.verify_webhook_signature(payload, expected_signature, secret) is True
        
        # Проверяем неправильную подпись
        assert SecurityUtils.verify_webhook_signature(payload, "wrong_signature", secret) is False

    def test_generate_idempotency_key(self):
        """Тест генерации ключа идемпотентности"""
        key = SecurityUtils.generate_idempotency_key()
        
        # Проверяем, что ключ генерируется
        assert len(key) > 0
        assert isinstance(key, str)


class TestRateLimiter:
    """Тесты для rate limiter"""

    def test_rate_limiter_initial_state(self):
        """Тест начального состояния rate limiter"""
        limiter = RateLimiter()
        client_id = "test_client"
        
        # В начальном состоянии запросы должны быть разрешены
        assert limiter.is_allowed(client_id, limit=1, window=3600) is True

    def test_rate_limiter_within_limit(self):
        """Тест rate limiter в пределах лимита"""
        limiter = RateLimiter()
        client_id = "test_client"
        
        # Первый запрос должен быть разрешен
        assert limiter.is_allowed(client_id, limit=2, window=3600) is True
        
        # Второй запрос должен быть разрешен
        assert limiter.is_allowed(client_id, limit=2, window=3600) is True

    def test_rate_limiter_exceed_limit(self):
        """Тест rate limiter при превышении лимита"""
        limiter = RateLimiter()
        client_id = "test_client"
        
        # Первый запрос
        assert limiter.is_allowed(client_id, limit=1, window=3600) is True
        
        # Второй запрос должен быть заблокирован
        assert limiter.is_allowed(client_id, limit=1, window=3600) is False

    def test_rate_limiter_window_expiry(self):
        """Тест истечения окна rate limiter"""
        limiter = RateLimiter()
        client_id = "test_client"
        
        # Первый запрос
        assert limiter.is_allowed(client_id, limit=1, window=1) is True
        
        # Второй запрос должен быть заблокирован
        assert limiter.is_allowed(client_id, limit=1, window=1) is False
        
        # Ждем истечения окна
        import time
        time.sleep(1.1)
        
        # После истечения окна запрос должен быть разрешен
        assert limiter.is_allowed(client_id, limit=1, window=1) is True


class TestSecurityMiddleware:
    """Тесты для middleware безопасности"""

    @pytest.fixture
    def mock_request(self):
        """Мок для HTTP запроса"""
        request = Mock()
        request.url.path = "/api/test"
        request.client.host = "127.0.0.1"
        request.headers = {}
        return request

    @pytest.fixture
    def mock_response(self):
        """Мок для HTTP ответа"""
        response = Mock()
        response.headers = {}
        response.status_code = 200
        return response

    def test_security_headers(self, mock_request, mock_response):
        """Тест добавления security headers"""
        from app.core.middleware import SecurityMiddleware
        
        middleware = SecurityMiddleware(Mock())
        
        # Мокаем call_next
        async def mock_call_next(request):
            return mock_response
        
        # Вызываем middleware
        import asyncio
        result = asyncio.run(middleware.dispatch(mock_request, mock_call_next))
        
        # Проверяем, что security headers добавлены
        assert "X-Content-Type-Options" in result.headers
        assert "X-Frame-Options" in result.headers
        assert "X-XSS-Protection" in result.headers
        assert "Referrer-Policy" in result.headers
        assert "Strict-Transport-Security" in result.headers


class TestWebhookSecurity:
    """Тесты для безопасности webhook"""

    def test_webhook_signature_validation(self):
        """Тест валидации подписи webhook"""
        from app.core.middleware import WebhookSignatureMiddleware
        
        middleware = WebhookSignatureMiddleware(Mock())
        
        # Создаем тестовые данные
        payload = '{"test": "data"}'
        secret = settings.amocrm_webhook_secret
        
        import hmac
        import hashlib
        signature = hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Мокаем запрос
        request = Mock()
        request.url.path = "/api/webhooks/amocrm"
        request.headers = {"X-Webhook-Signature": signature}
        request.body = lambda: payload.encode()
        
        # Мокаем call_next
        async def mock_call_next(request):
            return Mock()
        
        # Тестируем с правильной подписью
        import asyncio
        result = asyncio.run(middleware.dispatch(request, mock_call_next))
        
        # Должен вернуть нормальный ответ
        assert result is not None


class TestRetryLogic:
    """Тесты для retry логики"""

    def test_retry_success_on_first_attempt(self):
        """Тест успешного выполнения с первой попытки"""
        from app.core.retry import RetryConfig, RetryHandler
        
        config = RetryConfig(max_attempts=3, base_delay=0.1)
        handler = RetryHandler(config)
        
        # Функция, которая всегда успешна
        async def success_func():
            return "success"
        
        # Выполняем с retry
        import asyncio
        result = asyncio.run(handler.execute_with_retry(success_func))
        
        assert result == "success"

    def test_retry_success_after_failures(self):
        """Тест успешного выполнения после неудач"""
        from app.core.retry import RetryConfig, RetryHandler
        
        config = RetryConfig(max_attempts=3, base_delay=0.1)
        handler = RetryHandler(config)
        
        # Счетчик попыток
        attempts = 0
        
        async def failing_then_success():
            nonlocal attempts
            attempts += 1
            if attempts < 3:
                raise Exception("Temporary failure")
            return "success"
        
        # Выполняем с retry
        import asyncio
        result = asyncio.run(handler.execute_with_retry(failing_then_success))
        
        assert result == "success"
        assert attempts == 3

    def test_retry_max_attempts_exceeded(self):
        """Тест превышения максимального количества попыток"""
        from app.core.retry import RetryConfig, RetryHandler
        
        config = RetryConfig(max_attempts=2, base_delay=0.1)
        handler = RetryHandler(config)
        
        # Функция, которая всегда падает
        async def always_fail():
            raise Exception("Always fails")
        
        # Выполняем с retry
        import asyncio
        with pytest.raises(Exception, match="Always fails"):
            asyncio.run(handler.execute_with_retry(always_fail))


if __name__ == "__main__":
    pytest.main([__file__])
