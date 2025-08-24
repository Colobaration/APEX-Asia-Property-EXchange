"""
Unit тесты для сервисного слоя
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
from typing import List

from app.services.auth_service import AuthService
from app.services.lead_service import LeadService
from app.services.analytics_service import AnalyticsService
from app.services.notification_service import NotificationService
from app.core.exceptions import AuthenticationError, UserNotFoundError, LeadNotFoundError


class TestAuthService:
    """Тесты для AuthService"""

    @pytest.fixture
    def auth_service(self):
        """Фикстура для AuthService"""
        return AuthService()

    @pytest.fixture
    def mock_user(self):
        """Мок пользователя"""
        user = Mock()
        user.id = 1
        user.email = "test@example.com"
        user.full_name = "Test User"
        user.is_active = True
        user.is_superuser = False
        user.created_at = datetime.utcnow()
        return user

    def test_verify_password(self, auth_service):
        """Тест проверки пароля"""
        password = "test_password_123"
        hashed = auth_service.get_password_hash(password)
        
        assert auth_service.verify_password(password, hashed) is True
        assert auth_service.verify_password("wrong_password", hashed) is False

    def test_create_access_token(self, auth_service, mock_user):
        """Тест создания JWT токена"""
        token = auth_service.create_access_token(mock_user)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Проверяем, что токен может быть декодирован
        payload = auth_service.verify_token(token)
        assert payload is not None
        assert payload["sub"] == mock_user.id
        assert payload["email"] == mock_user.email

    def test_verify_token_invalid(self, auth_service):
        """Тест проверки недействительного токена"""
        payload = auth_service.verify_token("invalid.token.here")
        assert payload is None

    @patch('app.services.auth_service.get_user_by_email')
    async def test_authenticate_user_success(self, mock_get_user, auth_service, mock_user):
        """Тест успешной аутентификации пользователя"""
        mock_user.password_hash = auth_service.get_password_hash("test_password")
        mock_get_user.return_value = mock_user
        
        result = await auth_service.authenticate_user("test@example.com", "test_password")
        
        assert result == mock_user
        mock_get_user.assert_called_once_with("test@example.com")

    @patch('app.services.auth_service.get_user_by_email')
    async def test_authenticate_user_wrong_password(self, mock_get_user, auth_service, mock_user):
        """Тест аутентификации с неправильным паролем"""
        mock_user.password_hash = auth_service.get_password_hash("correct_password")
        mock_get_user.return_value = mock_user
        
        with pytest.raises(AuthenticationError):
            await auth_service.authenticate_user("test@example.com", "wrong_password")

    @patch('app.services.auth_service.get_user_by_email')
    async def test_authenticate_user_not_found(self, mock_get_user, auth_service):
        """Тест аутентификации несуществующего пользователя"""
        mock_get_user.return_value = None
        
        with pytest.raises(AuthenticationError):
            await auth_service.authenticate_user("nonexistent@example.com", "password")

    @patch('app.services.auth_service.get_user_by_email')
    async def test_authenticate_user_inactive(self, mock_get_user, auth_service, mock_user):
        """Тест аутентификации неактивного пользователя"""
        mock_user.is_active = False
        mock_user.password_hash = auth_service.get_password_hash("test_password")
        mock_get_user.return_value = mock_user
        
        with pytest.raises(AuthenticationError):
            await auth_service.authenticate_user("test@example.com", "test_password")


class TestLeadService:
    """Тесты для LeadService"""

    @pytest.fixture
    def lead_service(self):
        """Фикстура для LeadService"""
        return LeadService()

    @pytest.fixture
    def mock_lead(self):
        """Мок лида"""
        lead = Mock()
        lead.id = 1
        lead.first_name = "John"
        lead.last_name = "Doe"
        lead.email = "john@example.com"
        lead.phone = "+1234567890"
        lead.status = "new"
        lead.source = "website"
        lead.created_at = datetime.utcnow()
        lead.updated_at = datetime.utcnow()
        return lead

    @patch('app.services.lead_service.get_lead_by_id')
    async def test_get_lead_success(self, mock_get_lead, lead_service, mock_lead):
        """Тест успешного получения лида"""
        mock_get_lead.return_value = mock_lead
        
        result = await lead_service.get_lead(1)
        
        assert result == mock_lead
        mock_get_lead.assert_called_once_with(1)

    @patch('app.services.lead_service.get_lead_by_id')
    async def test_get_lead_not_found(self, mock_get_lead, lead_service):
        """Тест получения несуществующего лида"""
        mock_get_lead.return_value = None
        
        with pytest.raises(LeadNotFoundError):
            await lead_service.get_lead(999)

    @patch('app.services.lead_service.get_leads')
    async def test_get_leads_with_filters(self, mock_get_leads, lead_service, mock_lead):
        """Тест получения лидов с фильтрами"""
        mock_get_leads.return_value = [mock_lead]
        
        filters = {"status": "new", "source": "website"}
        result = await lead_service.get_leads(filters=filters)
        
        assert result == [mock_lead]
        mock_get_leads.assert_called_once_with(filters=filters)

    @patch('app.services.lead_service.create_lead')
    async def test_create_lead_success(self, mock_create_lead, lead_service, mock_lead):
        """Тест успешного создания лида"""
        mock_create_lead.return_value = mock_lead
        
        lead_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "phone": "+1234567890",
            "status": "new",
            "source": "website"
        }
        
        result = await lead_service.create_lead(lead_data)
        
        assert result == mock_lead
        mock_create_lead.assert_called_once_with(lead_data)

    @patch('app.services.lead_service.update_lead')
    async def test_update_lead_success(self, mock_update_lead, lead_service, mock_lead):
        """Тест успешного обновления лида"""
        mock_update_lead.return_value = mock_lead
        
        update_data = {"status": "contacted"}
        result = await lead_service.update_lead(1, update_data)
        
        assert result == mock_lead
        mock_update_lead.assert_called_once_with(1, update_data)

    @patch('app.services.lead_service.delete_lead')
    async def test_delete_lead_success(self, mock_delete_lead, lead_service):
        """Тест успешного удаления лида"""
        mock_delete_lead.return_value = True
        
        result = await lead_service.delete_lead(1)
        
        assert result is True
        mock_delete_lead.assert_called_once_with(1)

    @patch('app.services.lead_service.get_lead_statistics')
    async def test_get_lead_statistics(self, mock_get_stats, lead_service):
        """Тест получения статистики лидов"""
        mock_stats = {
            "total": 100,
            "new": 20,
            "contacted": 30,
            "qualified": 25,
            "closed_won": 15,
            "closed_lost": 10
        }
        mock_get_stats.return_value = mock_stats
        
        result = await lead_service.get_lead_statistics()
        
        assert result == mock_stats
        mock_get_stats.assert_called_once()


class TestAnalyticsService:
    """Тесты для AnalyticsService"""

    @pytest.fixture
    def analytics_service(self):
        """Фикстура для AnalyticsService"""
        return AnalyticsService()

    @patch('app.services.analytics_service.get_dashboard_data')
    async def test_get_dashboard_data(self, mock_get_dashboard, analytics_service):
        """Тест получения данных дашборда"""
        mock_data = {
            "total_leads": 100,
            "conversion_rate": 0.15,
            "revenue": 50000,
            "recent_activities": []
        }
        mock_get_dashboard.return_value = mock_data
        
        result = await analytics_service.get_dashboard_data()
        
        assert result == mock_data
        mock_get_dashboard.assert_called_once()

    @patch('app.services.analytics_service.get_lead_conversion_metrics')
    async def test_get_lead_conversion_metrics(self, mock_get_metrics, analytics_service):
        """Тест получения метрик конверсии лидов"""
        mock_metrics = {
            "conversion_rate": 0.15,
            "avg_time_to_convert": 7.5,
            "conversion_by_source": {}
        }
        mock_get_metrics.return_value = mock_metrics
        
        result = await analytics_service.get_lead_conversion_metrics()
        
        assert result == mock_metrics
        mock_get_metrics.assert_called_once()

    @patch('app.services.analytics_service.get_revenue_metrics')
    async def test_get_revenue_metrics(self, mock_get_revenue, analytics_service):
        """Тест получения метрик доходов"""
        mock_revenue = {
            "total_revenue": 50000,
            "avg_deal_size": 5000,
            "revenue_by_month": {}
        }
        mock_get_revenue.return_value = mock_revenue
        
        result = await analytics_service.get_revenue_metrics()
        
        assert result == mock_revenue
        mock_get_revenue.assert_called_once()

    @patch('app.services.analytics_service.get_performance_metrics')
    async def test_get_performance_metrics(self, mock_get_performance, analytics_service):
        """Тест получения метрик производительности"""
        mock_performance = {
            "response_time": 0.5,
            "uptime": 0.999,
            "error_rate": 0.001
        }
        mock_get_performance.return_value = mock_performance
        
        result = await analytics_service.get_performance_metrics()
        
        assert result == mock_performance
        mock_get_performance.assert_called_once()


class TestNotificationService:
    """Тесты для NotificationService"""

    @pytest.fixture
    def notification_service(self):
        """Фикстура для NotificationService"""
        return NotificationService()

    @pytest.fixture
    def mock_notification(self):
        """Мок уведомления"""
        notification = Mock()
        notification.id = 1
        notification.title = "Test Notification"
        notification.message = "Test message"
        notification.notification_type = "email"
        notification.status = "pending"
        notification.created_at = datetime.utcnow()
        return notification

    @patch('app.services.notification_service.create_notification')
    async def test_create_notification_success(self, mock_create, notification_service, mock_notification):
        """Тест успешного создания уведомления"""
        mock_create.return_value = mock_notification
        
        notification_data = {
            "title": "Test Notification",
            "message": "Test message",
            "notification_type": "email",
            "recipient_email": "test@example.com"
        }
        
        result = await notification_service.create_notification(notification_data)
        
        assert result == mock_notification
        mock_create.assert_called_once_with(notification_data)

    @patch('app.services.notification_service.get_notifications')
    async def test_get_notifications_with_filters(self, mock_get, notification_service, mock_notification):
        """Тест получения уведомлений с фильтрами"""
        mock_get.return_value = [mock_notification]
        
        filters = {"status": "pending", "notification_type": "email"}
        result = await notification_service.get_notifications(filters=filters)
        
        assert result == [mock_notification]
        mock_get.assert_called_once_with(filters=filters)

    @patch('app.services.notification_service.mark_notification_as_read')
    async def test_mark_notification_as_read(self, mock_mark_read, notification_service):
        """Тест отметки уведомления как прочитанного"""
        mock_mark_read.return_value = True
        
        result = await notification_service.mark_notification_as_read(1)
        
        assert result is True
        mock_mark_read.assert_called_once_with(1)

    @patch('app.services.notification_service.send_notification')
    async def test_send_notification_email(self, mock_send, notification_service, mock_notification):
        """Тест отправки email уведомления"""
        mock_send.return_value = True
        
        result = await notification_service.send_notification(mock_notification)
        
        assert result is True
        mock_send.assert_called_once_with(mock_notification)

    @patch('app.services.notification_service.get_notification_statistics')
    async def test_get_notification_statistics(self, mock_get_stats, notification_service):
        """Тест получения статистики уведомлений"""
        mock_stats = {
            "total": 100,
            "sent": 80,
            "failed": 5,
            "pending": 15
        }
        mock_get_stats.return_value = mock_stats
        
        result = await notification_service.get_notification_statistics()
        
        assert result == mock_stats
        mock_get_stats.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
