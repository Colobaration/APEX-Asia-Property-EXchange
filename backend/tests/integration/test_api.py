"""
Integration тесты для API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
import json

from app.main import app
from app.core.config import settings


@pytest.fixture
def client():
    """Фикстура для тестового клиента"""
    return TestClient(app)


@pytest.fixture
def mock_user():
    """Мок пользователя для тестов"""
    user = Mock()
    user.id = 1
    user.email = "test@example.com"
    user.full_name = "Test User"
    user.is_active = True
    user.is_superuser = False
    return user


@pytest.fixture
def mock_lead():
    """Мок лида для тестов"""
    lead = Mock()
    lead.id = 1
    lead.first_name = "John"
    lead.last_name = "Doe"
    lead.email = "john@example.com"
    lead.phone = "+1234567890"
    lead.status = "new"
    lead.source = "website"
    lead.created_at = "2024-01-01T00:00:00Z"
    lead.updated_at = "2024-01-01T00:00:00Z"
    return lead


class TestHealthEndpoint:
    """Тесты для health endpoint"""

    def test_health_check(self, client):
        """Тест health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "environment" in data
        assert "version" in data


class TestAuthEndpoints:
    """Тесты для endpoints аутентификации"""

    @patch('app.api.auth_v2.AuthService')
    def test_register_success(self, mock_auth_service, client):
        """Тест успешной регистрации"""
        mock_service = Mock()
        mock_auth_service.return_value = mock_service
        mock_service.register_user.return_value = {"id": 1, "email": "test@example.com"}
        
        response = client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "test_password_123",
                "full_name": "Test User"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"
        assert "user" in data["data"]

    @patch('app.api.auth_v2.AuthService')
    def test_register_invalid_data(self, mock_auth_service, client):
        """Тест регистрации с невалидными данными"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "invalid-email",
                "password": "123",  # слишком короткий
                "full_name": "Test User"
            }
        )
        
        assert response.status_code == 422

    @patch('app.api.auth_v2.AuthService')
    def test_login_success(self, mock_auth_service, client):
        """Тест успешного входа"""
        mock_service = Mock()
        mock_auth_service.return_value = mock_service
        mock_service.authenticate_user.return_value = {"id": 1, "email": "test@example.com"}
        mock_service.create_access_token.return_value = "test_token"
        
        response = client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "test_password_123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "access_token" in data["data"]

    @patch('app.api.auth_v2.AuthService')
    def test_login_invalid_credentials(self, mock_auth_service, client):
        """Тест входа с неверными учетными данными"""
        mock_service = Mock()
        mock_auth_service.return_value = mock_service
        mock_service.authenticate_user.side_effect = Exception("Invalid credentials")
        
        response = client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "wrong_password"
            }
        )
        
        assert response.status_code == 401

    @patch('app.api.auth_v2.get_current_active_user')
    @patch('app.api.auth_v2.AuthService')
    def test_get_profile(self, mock_auth_service, mock_get_user, client, mock_user):
        """Тест получения профиля пользователя"""
        mock_get_user.return_value = mock_user
        mock_service = Mock()
        mock_auth_service.return_value = mock_service
        mock_service.get_user_profile.return_value = mock_user
        
        # Мокаем токен
        with patch('app.core.security.SecurityUtils.verify_token') as mock_verify:
            mock_verify.return_value = {"sub": 1, "email": "test@example.com"}
            
            response = client.get(
                "/api/auth/profile",
                headers={"Authorization": "Bearer test_token"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"


class TestLeadsEndpoints:
    """Тесты для endpoints лидов"""

    @patch('app.api.leads_v2.get_current_active_user')
    @patch('app.api.leads_v2.LeadService')
    def test_get_leads(self, mock_lead_service, mock_get_user, client, mock_user):
        """Тест получения списка лидов"""
        mock_get_user.return_value = mock_user
        mock_service = Mock()
        mock_lead_service.return_value = mock_service
        mock_service.get_leads.return_value = {
            "data": [mock_lead],
            "total": 1,
            "page": 1,
            "per_page": 10
        }
        
        with patch('app.core.security.SecurityUtils.verify_token') as mock_verify:
            mock_verify.return_value = {"sub": 1, "email": "test@example.com"}
            
            response = client.get(
                "/api/leads",
                headers={"Authorization": "Bearer test_token"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data["data"]

    @patch('app.api.leads_v2.get_current_active_user')
    @patch('app.api.leads_v2.LeadService')
    def test_create_lead(self, mock_lead_service, mock_get_user, client, mock_user, mock_lead):
        """Тест создания лида"""
        mock_get_user.return_value = mock_user
        mock_service = Mock()
        mock_lead_service.return_value = mock_service
        mock_service.create_lead.return_value = mock_lead
        
        with patch('app.core.security.SecurityUtils.verify_token') as mock_verify:
            mock_verify.return_value = {"sub": 1, "email": "test@example.com"}
            
            response = client.post(
                "/api/leads",
                json={
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "john@example.com",
                    "phone": "+1234567890",
                    "status": "new",
                    "source": "website"
                },
                headers={"Authorization": "Bearer test_token"}
            )
        
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"

    @patch('app.api.leads_v2.get_current_active_user')
    @patch('app.api.leads_v2.LeadService')
    def test_get_lead(self, mock_lead_service, mock_get_user, client, mock_user, mock_lead):
        """Тест получения конкретного лида"""
        mock_get_user.return_value = mock_user
        mock_service = Mock()
        mock_lead_service.return_value = mock_service
        mock_service.get_lead.return_value = mock_lead
        
        with patch('app.core.security.SecurityUtils.verify_token') as mock_verify:
            mock_verify.return_value = {"sub": 1, "email": "test@example.com"}
            
            response = client.get(
                "/api/leads/1",
                headers={"Authorization": "Bearer test_token"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    @patch('app.api.leads_v2.get_current_active_user')
    @patch('app.api.leads_v2.LeadService')
    def test_update_lead(self, mock_lead_service, mock_get_user, client, mock_user, mock_lead):
        """Тест обновления лида"""
        mock_get_user.return_value = mock_user
        mock_service = Mock()
        mock_lead_service.return_value = mock_service
        mock_service.update_lead.return_value = mock_lead
        
        with patch('app.core.security.SecurityUtils.verify_token') as mock_verify:
            mock_verify.return_value = {"sub": 1, "email": "test@example.com"}
            
            response = client.put(
                "/api/leads/1",
                json={"status": "contacted"},
                headers={"Authorization": "Bearer test_token"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    @patch('app.api.leads_v2.get_current_active_user')
    @patch('app.api.leads_v2.LeadService')
    def test_delete_lead(self, mock_lead_service, mock_get_user, client, mock_user):
        """Тест удаления лида"""
        mock_get_user.return_value = mock_user
        mock_service = Mock()
        mock_lead_service.return_value = mock_service
        mock_service.delete_lead.return_value = True
        
        with patch('app.core.security.SecurityUtils.verify_token') as mock_verify:
            mock_verify.return_value = {"sub": 1, "email": "test@example.com"}
            
            response = client.delete(
                "/api/leads/1",
                headers={"Authorization": "Bearer test_token"}
            )
        
        assert response.status_code == 204


class TestAnalyticsEndpoints:
    """Тесты для endpoints аналитики"""

    @patch('app.api.analytics.get_current_active_user')
    @patch('app.api.analytics.AnalyticsService')
    def test_get_dashboard_data(self, mock_analytics_service, mock_get_user, client, mock_user):
        """Тест получения данных дашборда"""
        mock_get_user.return_value = mock_user
        mock_service = Mock()
        mock_analytics_service.return_value = mock_service
        mock_service.get_dashboard_data.return_value = {
            "total_leads": 100,
            "conversion_rate": 0.15,
            "revenue": 50000
        }
        
        with patch('app.core.security.SecurityUtils.verify_token') as mock_verify:
            mock_verify.return_value = {"sub": 1, "email": "test@example.com"}
            
            response = client.get(
                "/api/analytics/dashboard",
                headers={"Authorization": "Bearer test_token"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"


class TestNotificationsEndpoints:
    """Тесты для endpoints уведомлений"""

    @patch('app.api.notifications.get_current_active_user')
    @patch('app.api.notifications.NotificationService')
    def test_get_notifications(self, mock_notification_service, mock_get_user, client, mock_user):
        """Тест получения уведомлений"""
        mock_get_user.return_value = mock_user
        mock_service = Mock()
        mock_notification_service.return_value = mock_service
        mock_service.get_notifications.return_value = {
            "data": [],
            "total": 0,
            "page": 1,
            "per_page": 10
        }
        
        with patch('app.core.security.SecurityUtils.verify_token') as mock_verify:
            mock_verify.return_value = {"sub": 1, "email": "test@example.com"}
            
            response = client.get(
                "/api/notifications",
                headers={"Authorization": "Bearer test_token"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"


class TestWebhookEndpoints:
    """Тесты для webhook endpoints"""

    def test_amocrm_webhook_with_signature(self, client):
        """Тест webhook с правильной подписью"""
        payload = '{"test": "data"}'
        
        # Создаем правильную подпись
        import hmac
        import hashlib
        secret = settings.amocrm_webhook_secret
        signature = hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        response = client.post(
            "/api/webhooks/amocrm",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "X-Webhook-Signature": signature
            }
        )
        
        # Должен вернуть 200 или 201 в зависимости от логики
        assert response.status_code in [200, 201]

    def test_amocrm_webhook_without_signature(self, client):
        """Тест webhook без подписи"""
        response = client.post(
            "/api/webhooks/amocrm",
            json={"test": "data"},
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 401

    def test_amocrm_webhook_invalid_signature(self, client):
        """Тест webhook с неправильной подписью"""
        response = client.post(
            "/api/webhooks/amocrm",
            json={"test": "data"},
            headers={
                "Content-Type": "application/json",
                "X-Webhook-Signature": "invalid_signature"
            }
        )
        
        assert response.status_code == 401


class TestErrorHandling:
    """Тесты для обработки ошибок"""

    def test_404_not_found(self, client):
        """Тест 404 ошибки"""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404

    def test_422_validation_error(self, client):
        """Тест ошибки валидации"""
        response = client.post(
            "/api/auth/register",
            json={"invalid": "data"}
        )
        assert response.status_code == 422

    def test_500_internal_error(self, client):
        """Тест внутренней ошибки сервера"""
        # Создаем endpoint, который вызывает исключение
        @app.get("/test-error")
        def test_error():
            raise Exception("Test error")
        
        response = client.get("/test-error")
        assert response.status_code == 500


class TestRateLimiting:
    """Тесты для rate limiting"""

    def test_rate_limit_exceeded(self, client):
        """Тест превышения rate limit"""
        # Отправляем много запросов подряд
        for i in range(110):  # Больше лимита в 100
            response = client.get("/api/leads")
            if response.status_code == 429:
                break
        
        # Должен получить 429 после превышения лимита
        assert response.status_code == 429


if __name__ == "__main__":
    pytest.main([__file__])
