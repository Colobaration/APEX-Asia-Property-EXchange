"""
Performance тесты для APEX
"""

import pytest
import asyncio
import time
import statistics
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any
import aiohttp
import asyncio

from app.main import app
from app.core.config import settings


class PerformanceTestConfig:
    """Конфигурация для performance тестов"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.timeout = 30
        self.max_concurrent_requests = 100
        self.test_duration = 60  # секунды
        self.expected_response_time = 1.0  # секунды
        self.expected_throughput = 100  # запросов в секунду


class PerformanceMetrics:
    """Метрики производительности"""
    
    def __init__(self):
        self.response_times: List[float] = []
        self.status_codes: List[int] = []
        self.errors: List[str] = []
        self.start_time = time.time()
        self.end_time = None
    
    def add_response(self, response_time: float, status_code: int, error: str = None):
        """Добавить результат запроса"""
        self.response_times.append(response_time)
        self.status_codes.append(status_code)
        if error:
            self.errors.append(error)
    
    def finish(self):
        """Завершить сбор метрик"""
        self.end_time = time.time()
    
    @property
    def total_requests(self) -> int:
        """Общее количество запросов"""
        return len(self.response_times)
    
    @property
    def successful_requests(self) -> int:
        """Количество успешных запросов"""
        return len([code for code in self.status_codes if 200 <= code < 300])
    
    @property
    def error_rate(self) -> float:
        """Процент ошибок"""
        if not self.total_requests:
            return 0.0
        return (self.total_requests - self.successful_requests) / self.total_requests * 100
    
    @property
    def avg_response_time(self) -> float:
        """Среднее время ответа"""
        if not self.response_times:
            return 0.0
        return statistics.mean(self.response_times)
    
    @property
    def median_response_time(self) -> float:
        """Медианное время ответа"""
        if not self.response_times:
            return 0.0
        return statistics.median(self.response_times)
    
    @property
    def p95_response_time(self) -> float:
        """95-й процентиль времени ответа"""
        if not self.response_times:
            return 0.0
        return statistics.quantiles(self.response_times, n=20)[18]  # 95-й процентиль
    
    @property
    def p99_response_time(self) -> float:
        """99-й процентиль времени ответа"""
        if not self.response_times:
            return 0.0
        return statistics.quantiles(self.response_times, n=100)[98]  # 99-й процентиль
    
    @property
    def throughput(self) -> float:
        """Пропускная способность (запросов в секунду)"""
        if not self.end_time or not self.start_time:
            return 0.0
        duration = self.end_time - self.start_time
        if duration <= 0:
            return 0.0
        return self.total_requests / duration
    
    def get_summary(self) -> Dict[str, Any]:
        """Получить сводку метрик"""
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "error_rate": f"{self.error_rate:.2f}%",
            "avg_response_time": f"{self.avg_response_time:.3f}s",
            "median_response_time": f"{self.median_response_time:.3f}s",
            "p95_response_time": f"{self.p95_response_time:.3f}s",
            "p99_response_time": f"{self.p99_response_time:.3f}s",
            "throughput": f"{self.throughput:.2f} req/s",
            "total_errors": len(self.errors)
        }


class TestPerformance:
    """Performance тесты"""
    
    @pytest.fixture
    def config(self):
        """Конфигурация для тестов"""
        return PerformanceTestConfig()
    
    @pytest.fixture
    def metrics(self):
        """Метрики производительности"""
        return PerformanceMetrics()
    
    async def make_request(self, session: aiohttp.ClientSession, url: str) -> tuple:
        """Выполнить HTTP запрос"""
        start_time = time.time()
        try:
            async with session.get(url, timeout=self.config.timeout) as response:
                response_time = time.time() - start_time
                return response_time, response.status, None
        except Exception as e:
            response_time = time.time() - start_time
            return response_time, 0, str(e)
    
    async def load_test_endpoint(self, endpoint: str, config: PerformanceTestConfig, metrics: PerformanceMetrics):
        """Нагрузочное тестирование endpoint"""
        async with aiohttp.ClientSession() as session:
            url = f"{config.base_url}{endpoint}"
            
            # Создаем задачи для concurrent запросов
            tasks = []
            for _ in range(config.max_concurrent_requests):
                task = asyncio.create_task(self.make_request(session, url))
                tasks.append(task)
            
            # Выполняем запросы
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Собираем метрики
            for result in results:
                if isinstance(result, Exception):
                    metrics.add_response(0, 0, str(result))
                else:
                    response_time, status_code, error = result
                    metrics.add_response(response_time, status_code, error)
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_health_endpoint_performance(self, config, metrics):
        """Тест производительности health endpoint"""
        await self.load_test_endpoint("/health", config, metrics)
        metrics.finish()
        
        # Проверяем метрики
        assert metrics.error_rate < 5.0, f"Error rate too high: {metrics.error_rate}%"
        assert metrics.avg_response_time < config.expected_response_time, f"Response time too high: {metrics.avg_response_time}s"
        assert metrics.throughput > config.expected_throughput * 0.5, f"Throughput too low: {metrics.throughput} req/s"
        
        print(f"Health endpoint performance: {metrics.get_summary()}")
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_api_endpoints_performance(self, config, metrics):
        """Тест производительности API endpoints"""
        endpoints = [
            "/api/leads",
            "/api/analytics/dashboard",
            "/api/notifications"
        ]
        
        for endpoint in endpoints:
            endpoint_metrics = PerformanceMetrics()
            await self.load_test_endpoint(endpoint, config, endpoint_metrics)
            endpoint_metrics.finish()
            
            # Проверяем метрики для каждого endpoint
            assert endpoint_metrics.error_rate < 10.0, f"Error rate too high for {endpoint}: {endpoint_metrics.error_rate}%"
            assert endpoint_metrics.avg_response_time < config.expected_response_time * 2, f"Response time too high for {endpoint}: {endpoint_metrics.avg_response_time}s"
            
            print(f"{endpoint} performance: {endpoint_metrics.get_summary()}")
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_users_performance(self, config, metrics):
        """Тест производительности при одновременных пользователях"""
        # Симулируем 50 одновременных пользователей
        num_users = 50
        requests_per_user = 10
        
        async def user_session():
            """Сессия одного пользователя"""
            async with aiohttp.ClientSession() as session:
                user_metrics = PerformanceMetrics()
                
                # Пользователь выполняет несколько запросов
                for _ in range(requests_per_user):
                    response_time, status_code, error = await self.make_request(session, f"{config.base_url}/api/leads")
                    user_metrics.add_response(response_time, status_code, error)
                    await asyncio.sleep(0.1)  # Небольшая пауза между запросами
                
                return user_metrics
        
        # Запускаем сессии пользователей
        user_tasks = [asyncio.create_task(user_session()) for _ in range(num_users)]
        user_results = await asyncio.gather(*user_tasks)
        
        # Агрегируем метрики всех пользователей
        for user_metrics in user_results:
            metrics.response_times.extend(user_metrics.response_times)
            metrics.status_codes.extend(user_metrics.status_codes)
            metrics.errors.extend(user_metrics.errors)
        
        metrics.finish()
        
        # Проверяем метрики
        assert metrics.error_rate < 5.0, f"Error rate too high: {metrics.error_rate}%"
        assert metrics.avg_response_time < config.expected_response_time * 1.5, f"Response time too high: {metrics.avg_response_time}s"
        
        print(f"Concurrent users performance: {metrics.get_summary()}")
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_database_performance(self, config, metrics):
        """Тест производительности базы данных"""
        # Тестируем операции с лидами
        async with aiohttp.ClientSession() as session:
            # Создание лидов
            create_tasks = []
            for i in range(10):
                lead_data = {
                    "first_name": f"Test{i}",
                    "last_name": f"User{i}",
                    "email": f"test{i}@example.com",
                    "phone": f"+123456789{i}",
                    "status": "new",
                    "source": "website"
                }
                task = asyncio.create_task(
                    session.post(f"{config.base_url}/api/leads", json=lead_data)
                )
                create_tasks.append(task)
            
            create_results = await asyncio.gather(*create_tasks, return_exceptions=True)
            
            # Собираем метрики создания
            for result in create_results:
                if isinstance(result, Exception):
                    metrics.add_response(0, 0, str(result))
                else:
                    metrics.add_response(0, result.status, None)
            
            # Чтение лидов
            read_tasks = []
            for _ in range(20):
                task = asyncio.create_task(
                    session.get(f"{config.base_url}/api/leads")
                )
                read_tasks.append(task)
            
            read_results = await asyncio.gather(*read_tasks, return_exceptions=True)
            
            # Собираем метрики чтения
            for result in read_results:
                if isinstance(result, Exception):
                    metrics.add_response(0, 0, str(result))
                else:
                    metrics.add_response(0, result.status, None)
        
        metrics.finish()
        
        # Проверяем метрики
        assert metrics.error_rate < 10.0, f"Database error rate too high: {metrics.error_rate}%"
        
        print(f"Database performance: {metrics.get_summary()}")
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_memory_usage(self, config):
        """Тест использования памяти"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Выполняем нагрузочное тестирование
        metrics = PerformanceMetrics()
        await self.load_test_endpoint("/api/leads", config, metrics)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Проверяем, что увеличение памяти не превышает 100MB
        assert memory_increase < 100, f"Memory usage increased too much: {memory_increase:.2f}MB"
        
        print(f"Memory usage: {initial_memory:.2f}MB -> {final_memory:.2f}MB (increase: {memory_increase:.2f}MB)")
    
    @pytest.mark.performance
    def test_cpu_usage(self, config):
        """Тест использования CPU"""
        import psutil
        import time
        
        process = psutil.Process()
        
        # Измеряем CPU usage в течение 10 секунд
        cpu_percentages = []
        for _ in range(10):
            cpu_percent = process.cpu_percent(interval=1)
            cpu_percentages.append(cpu_percent)
        
        avg_cpu = statistics.mean(cpu_percentages)
        max_cpu = max(cpu_percentages)
        
        # Проверяем, что среднее использование CPU не превышает 80%
        assert avg_cpu < 80, f"Average CPU usage too high: {avg_cpu:.2f}%"
        
        print(f"CPU usage: avg={avg_cpu:.2f}%, max={max_cpu:.2f}%")


class TestLoadTesting:
    """Нагрузочное тестирование"""
    
    @pytest.mark.load
    @pytest.mark.asyncio
    async def test_sustained_load(self):
        """Тест устойчивой нагрузки"""
        config = PerformanceTestConfig()
        config.test_duration = 300  # 5 минут
        config.max_concurrent_requests = 50
        
        metrics = PerformanceMetrics()
        
        # Запускаем нагрузку на 5 минут
        start_time = time.time()
        while time.time() - start_time < config.test_duration:
            await self.load_test_endpoint("/api/leads", config, metrics)
            await asyncio.sleep(1)
        
        metrics.finish()
        
        # Проверяем стабильность
        assert metrics.error_rate < 5.0, f"Error rate too high during sustained load: {metrics.error_rate}%"
        assert metrics.avg_response_time < 2.0, f"Response time degraded: {metrics.avg_response_time}s"
        
        print(f"Sustained load test: {metrics.get_summary()}")
    
    @pytest.mark.load
    @pytest.mark.asyncio
    async def test_spike_load(self):
        """Тест пиковой нагрузки"""
        config = PerformanceTestConfig()
        config.max_concurrent_requests = 200  # Высокая нагрузка
        
        metrics = PerformanceMetrics()
        
        # Резкий всплеск нагрузки
        await self.load_test_endpoint("/api/leads", config, metrics)
        metrics.finish()
        
        # Проверяем, что система справляется с пиковой нагрузкой
        assert metrics.error_rate < 20.0, f"Error rate too high during spike: {metrics.error_rate}%"
        assert metrics.throughput > 50, f"Throughput too low during spike: {metrics.throughput} req/s"
        
        print(f"Spike load test: {metrics.get_summary()}")


if __name__ == "__main__":
    pytest.main([__file__, "-m", "performance"])
