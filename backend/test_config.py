#!/usr/bin/env python3
"""
Скрипт для тестирования конфигурации backend
"""

import os
import sys
from pathlib import Path

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent))

def test_config():
    """Тестирует загрузку конфигурации"""
    try:
        from app.core.config import settings
        print("✅ Конфигурация загружена успешно!")
        print(f"Environment: {settings.environment}")
        print(f"Debug: {settings.debug}")
        print(f"Allowed hosts: {settings.allowed_hosts}")
        print(f"CORS origins: {settings.cors_origins}")
        print(f"Database URL: {settings.db_url}")
        print(f"Redis URL: {settings.redis_url}")
        return True
    except Exception as e:
        print(f"❌ Ошибка загрузки конфигурации: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_environment_variables():
    """Тестирует переменные окружения"""
    print("\n🔍 Проверка переменных окружения:")
    
    # Устанавливаем тестовые переменные
    os.environ['ENVIRONMENT'] = 'staging'
    os.environ['ALLOWED_HOSTS'] = 'localhost,127.0.0.1,*.apex-asia.com'
    os.environ['CORS_ORIGINS'] = 'http://localhost:3000,https://staging.apex-asia.com'
    
    try:
        from app.core.config import settings
        print("✅ Переменные окружения обработаны успешно!")
        print(f"Allowed hosts: {settings.allowed_hosts}")
        print(f"CORS origins: {settings.cors_origins}")
        return True
    except Exception as e:
        print(f"❌ Ошибка обработки переменных окружения: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Тестирование конфигурации backend...")
    
    success1 = test_config()
    success2 = test_environment_variables()
    
    if success1 and success2:
        print("\n🎉 Все тесты прошли успешно!")
        sys.exit(0)
    else:
        print("\n💥 Некоторые тесты не прошли!")
        sys.exit(1)
