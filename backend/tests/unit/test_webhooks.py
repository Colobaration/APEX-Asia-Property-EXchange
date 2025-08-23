import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.api.webhooks import (
    verify_webhook_signature,
    validate_webhook_data,
    _extract_utm_data,
    _map_amo_status
)
from app.main import app

client = TestClient(app)

class TestWebhookSignature:
    """Тесты для проверки подписи webhook"""
    
    def test_valid_signature(self):
        """Тест валидной подписи"""
        client_uuid = "test-uuid"
        account_id = "test-account"
        client_secret = "test-secret"
        
        # Создаем правильную подпись
        import hashlib
        import hmac
        message = f"{client_uuid}|{account_id}"
        expected_signature = hmac.new(
            client_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        result = verify_webhook_signature(
            client_uuid, expected_signature, account_id, client_secret
        )
        assert result is True
    
    def test_invalid_signature(self):
        """Тест невалидной подписи"""
        result = verify_webhook_signature(
            "test-uuid", "invalid-signature", "test-account", "test-secret"
        )
        assert result is False
    
    def test_missing_parameters(self):
        """Тест отсутствующих параметров"""
        result = verify_webhook_signature(
            None, "signature", "account", "secret"
        )
        assert result is False

class TestWebhookDataValidation:
    """Тесты для валидации данных webhook"""
    
    def test_valid_webhook_data(self):
        """Тест валидных данных webhook"""
        data = {
            "leads": {
                "add": [{"id": 1, "name": "Test Lead"}],
                "update": []
            },
            "contacts": {
                "add": []
            }
        }
        assert validate_webhook_data(data) is True
    
    def test_invalid_webhook_data(self):
        """Тест невалидных данных webhook"""
        data = {
            "leads": {
                "add": "not-a-list"  # Должен быть список
            }
        }
        assert validate_webhook_data(data) is False
    
    def test_empty_webhook_data(self):
        """Тест пустых данных webhook"""
        data = {}
        assert validate_webhook_data(data) is False

class TestUTMExtraction:
    """Тесты для извлечения UTM меток"""
    
    def test_extract_utm_data(self):
        """Тест извлечения UTM меток"""
        data = {
            "custom_fields_values": [
                {
                    "field_id": 123458,
                    "values": [{"value": "google"}]
                },
                {
                    "field_id": 123459,
                    "values": [{"value": "cpc"}]
                },
                {
                    "field_id": 123460,
                    "values": [{"value": "asia_deals"}]
                }
            ]
        }
        
        utm_data = _extract_utm_data(data)
        
        assert utm_data["utm_source"] == "google"
        assert utm_data["utm_medium"] == "cpc"
        assert utm_data["utm_campaign"] == "asia_deals"
    
    def test_extract_utm_data_empty(self):
        """Тест извлечения UTM меток из пустых данных"""
        data = {}
        utm_data = _extract_utm_data(data)
        assert utm_data == {}
    
    def test_extract_utm_data_no_values(self):
        """Тест извлечения UTM меток без значений"""
        data = {
            "custom_fields_values": [
                {
                    "field_id": 123458,
                    "values": []
                }
            ]
        }
        utm_data = _extract_utm_data(data)
        assert utm_data == {}

class TestStatusMapping:
    """Тесты для маппинга статусов"""
    
    def test_map_amo_status_valid(self):
        """Тест валидного маппинга статусов"""
        assert _map_amo_status(1) == "new"
        assert _map_amo_status(2) == "contacted"
        assert _map_amo_status(3) == "presentation"
        assert _map_amo_status(4) == "object_selected"
        assert _map_amo_status(5) == "reserved"
        assert _map_amo_status(6) == "deal"
        assert _map_amo_status(7) == "completed"
    
    def test_map_amo_status_invalid(self):
        """Тест невалидного статуса"""
        assert _map_amo_status(999) == "new"  # Возвращает дефолтный статус

class TestWebhookEndpoints:
    """Тесты для webhook endpoints"""
    
    @patch('app.api.webhooks.AmoCRMAuth')
    def test_webhook_test_endpoint(self, mock_auth):
        """Тест тестового endpoint"""
        response = client.get("/api/webhooks/amo/test")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert "timestamp" in data
        assert "supported_events" in data
    
    @patch('app.api.webhooks.get_db')
    def test_webhook_health_endpoint(self, mock_get_db):
        """Тест health check endpoint"""
        # Мокаем БД
        mock_db = Mock()
        mock_db.execute.return_value = None
        mock_get_db.return_value = iter([mock_db])
        
        response = client.get("/api/webhooks/amo/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
    
    @patch('app.api.webhooks.get_db')
    @patch('app.api.webhooks.AmoCRMAuth')
    def test_webhook_health_endpoint_db_error(self, mock_auth, mock_get_db):
        """Тест health check endpoint с ошибкой БД"""
        # Мокаем ошибку БД
        mock_get_db.side_effect = Exception("DB Error")
        
        response = client.get("/api/webhooks/amo/health")
        assert response.status_code == 503

class TestWebhookProcessing:
    """Тесты для обработки webhook"""
    
    @patch('app.api.webhooks.get_db')
    @patch('app.api.webhooks.AmoCRMAuth')
    def test_webhook_invalid_signature(self, mock_auth, mock_get_db):
        """Тест webhook с невалидной подписью"""
        # Мокаем проверку подписи
        mock_auth_instance = Mock()
        mock_auth_instance.client_secret = "test-secret"
        mock_auth.return_value = mock_auth_instance
        
        # Мокаем БД
        mock_db = Mock()
        mock_get_db.return_value = iter([mock_db])
        
        headers = {
            "X-Client-UUID": "test-uuid",
            "X-Signature": "invalid-signature",
            "X-Account-ID": "test-account"
        }
        
        response = client.post(
            "/api/webhooks/amo",
            json={"leads": {"add": []}},
            headers=headers
        )
        
        assert response.status_code == 401
    
    @patch('app.api.webhooks.get_db')
    @patch('app.api.webhooks.AmoCRMAuth')
    def test_webhook_invalid_data_structure(self, mock_auth, mock_get_db):
        """Тест webhook с невалидной структурой данных"""
        # Мокаем проверку подписи
        mock_auth_instance = Mock()
        mock_auth_instance.client_secret = "test-secret"
        mock_auth.return_value = mock_auth_instance
        
        # Мокаем БД
        mock_db = Mock()
        mock_get_db.return_value = iter([mock_db])
        
        headers = {
            "X-Client-UUID": "test-uuid",
            "X-Signature": "valid-signature",
            "X-Account-ID": "test-account"
        }
        
        # Создаем валидную подпись
        import hashlib
        import hmac
        message = "test-uuid|test-account"
        valid_signature = hmac.new(
            "test-secret".encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        headers["X-Signature"] = valid_signature
        
        response = client.post(
            "/api/webhooks/amo",
            json={"invalid": "data"},
            headers=headers
        )
        
        assert response.status_code == 400

if __name__ == "__main__":
    pytest.main([__file__])
