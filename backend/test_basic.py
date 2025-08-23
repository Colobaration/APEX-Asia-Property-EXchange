#!/usr/bin/env python3
"""
Простой тест для проверки базовой функциональности приложения
"""

import os
import sys
import asyncio
from unittest.mock import Mock, patch

# Устанавливаем переменные окружения для тестов
os.environ.update({
    'AMOCRM_CLIENT_ID': 'test_client_id',
    'AMOCRM_CLIENT_SECRET': 'test_client_secret',
    'SECRET_KEY': 'test_secret_key_for_testing_only',
    'JWT_SECRET': 'test_jwt_secret_for_testing_only',
    'DB_URL': 'sqlite:///:memory:',
    'FRONTEND_URL': 'http://localhost:3000'
})

def test_config_loading():
    """Тест загрузки конфигурации"""
    try:
        from app.core.config import settings
        assert settings.amocrm_client_id == 'test_client_id'
        assert settings.amocrm_client_secret == 'test_client_secret'
        assert settings.secret_key == 'test_secret_key_for_testing_only'
        assert settings.jwt_secret == 'test_jwt_secret_for_testing_only'
        print("✅ Конфигурация загружается корректно")
        return True
    except Exception as e:
        print(f"❌ Ошибка загрузки конфигурации: {e}")
        return False

def test_models_import():
    """Тест импорта моделей"""
    try:
        from app.models import lead, deal, amocrm_token
        print("✅ Модели импортируются корректно")
        return True
    except Exception as e:
        print(f"❌ Ошибка импорта моделей: {e}")
        return False

def test_api_import():
    """Тест импорта API модулей"""
    try:
        from app.api import leads, auth, webhooks, analytics
        print("✅ API модули импортируются корректно")
        return True
    except Exception as e:
        print(f"❌ Ошибка импорта API модулей: {e}")
        return False

def test_main_app():
    """Тест создания основного приложения"""
    try:
        from app.main import app
        assert app is not None
        print("✅ Основное приложение создается корректно")
        return True
    except Exception as e:
        print(f"❌ Ошибка создания приложения: {e}")
        return False

def test_utils():
    """Тест утилит"""
    try:
        from app.core.utils import validate_phone, validate_email
        print("✅ Утилиты импортируются корректно")
        return True
    except Exception as e:
        print(f"❌ Ошибка импорта утилит: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🔍 Запуск базовых тестов...")
    print("=" * 50)
    
    tests = [
        test_config_loading,
        test_models_import,
        test_api_import,
        test_main_app,
        test_utils
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Критическая ошибка в тесте {test.__name__}: {e}")
    
    print("=" * 50)
    print(f"📊 Результаты: {passed}/{total} тестов прошли успешно")
    
    if passed == total:
        print("🎉 Все базовые тесты прошли успешно!")
        return 0
    else:
        print("⚠️  Некоторые тесты не прошли")
        return 1

if __name__ == "__main__":
    sys.exit(main())
