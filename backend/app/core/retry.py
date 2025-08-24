"""
Модуль для retry логики с exponential backoff
"""

import asyncio
import time
from typing import Callable, Any, Optional, Type, Union, List
from functools import wraps
import random


class RetryConfig:
    """Конфигурация для retry логики"""
    
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        retry_exceptions: Optional[List[Type[Exception]]] = None
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.retry_exceptions = retry_exceptions or [Exception]


class RetryHandler:
    """Обработчик retry логики"""
    
    def __init__(self, config: RetryConfig):
        self.config = config
    
    def calculate_delay(self, attempt: int) -> float:
        """Вычисление задержки с exponential backoff"""
        delay = self.config.base_delay * (self.config.exponential_base ** (attempt - 1))
        
        # Ограничиваем максимальной задержкой
        delay = min(delay, self.config.max_delay)
        
        # Добавляем jitter для предотвращения thundering herd
        if self.config.jitter:
            delay = delay * (0.5 + random.random() * 0.5)
        
        return delay
    
    async def execute_with_retry(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """Выполнение функции с retry логикой"""
        last_exception = None
        
        for attempt in range(1, self.config.max_attempts + 1):
            try:
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                return result
                
            except tuple(self.config.retry_exceptions) as e:
                last_exception = e
                
                if attempt == self.config.max_attempts:
                    # Последняя попытка, пробрасываем исключение
                    raise last_exception
                
                # Вычисляем задержку
                delay = self.calculate_delay(attempt)
                
                # Логируем попытку
                from app.core.logging import logger
                logger.warning(
                    f"Retry attempt {attempt}/{self.config.max_attempts} failed: {str(e)}. "
                    f"Retrying in {delay:.2f} seconds..."
                )
                
                # Ждем перед следующей попыткой
                await asyncio.sleep(delay)
        
        # Не должны сюда дойти
        raise last_exception


def retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retry_exceptions: Optional[List[Type[Exception]]] = None
):
    """Декоратор для retry логики"""
    
    def decorator(func: Callable) -> Callable:
        config = RetryConfig(
            max_attempts=max_attempts,
            base_delay=base_delay,
            max_delay=max_delay,
            exponential_base=exponential_base,
            jitter=jitter,
            retry_exceptions=retry_exceptions
        )
        
        handler = RetryHandler(config)
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await handler.execute_with_retry(func, *args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Для синхронных функций создаем event loop
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            return loop.run_until_complete(
                handler.execute_with_retry(func, *args, **kwargs)
            )
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


class CircuitBreaker:
    """Circuit Breaker паттерн для защиты от каскадных сбоев"""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: Type[Exception] = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Выполнение функции с circuit breaker"""
        
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            self.on_success()
            return result
            
        except self.expected_exception as e:
            self.on_failure()
            raise e
    
    def on_success(self):
        """Обработка успешного выполнения"""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def on_failure(self):
        """Обработка неудачного выполнения"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"


# Предустановленные конфигурации
HTTP_RETRY_CONFIG = RetryConfig(
    max_attempts=3,
    base_delay=1.0,
    max_delay=30.0,
    exponential_base=2.0,
    jitter=True,
    retry_exceptions=[ConnectionError, TimeoutError]
)

DATABASE_RETRY_CONFIG = RetryConfig(
    max_attempts=5,
    base_delay=0.5,
    max_delay=10.0,
    exponential_base=1.5,
    jitter=True,
    retry_exceptions=[Exception]
)

EXTERNAL_API_RETRY_CONFIG = RetryConfig(
    max_attempts=3,
    base_delay=2.0,
    max_delay=60.0,
    exponential_base=2.0,
    jitter=True,
    retry_exceptions=[ConnectionError, TimeoutError, Exception]
)


# Утилиты для работы с retry
def http_retry(func: Callable) -> Callable:
    """Декоратор для HTTP запросов с retry"""
    return retry(
        max_attempts=3,
        base_delay=1.0,
        max_delay=30.0,
        exponential_base=2.0,
        jitter=True,
        retry_exceptions=[ConnectionError, TimeoutError]
    )(func)


def database_retry(func: Callable) -> Callable:
    """Декоратор для операций с БД с retry"""
    return retry(
        max_attempts=5,
        base_delay=0.5,
        max_delay=10.0,
        exponential_base=1.5,
        jitter=True,
        retry_exceptions=[Exception]
    )(func)


def external_api_retry(func: Callable) -> Callable:
    """Декоратор для внешних API с retry"""
    return retry(
        max_attempts=3,
        base_delay=2.0,
        max_delay=60.0,
        exponential_base=2.0,
        jitter=True,
        retry_exceptions=[ConnectionError, TimeoutError, Exception]
    )(func)
