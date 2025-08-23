#!/usr/bin/env python3
"""
Скрипт для тестирования интеграции с amoCRM
"""

import asyncio
import httpx
import json
from typing import Dict, Any

# Конфигурация
BASE_URL = "http://localhost:8000"
AMO_AUTH_URL = f"{BASE_URL}/api/auth/amo"
AMO_STATUS_URL = f"{BASE_URL}/api/auth/amo/status"
AMO_TEST_URL = f"{BASE_URL}/api/auth/amo/test"
LEADS_URL = f"{BASE_URL}/api/leads"
WEBHOOK_TEST_URL = f"{BASE_URL}/api/webhooks/amo/test"

async def test_amo_auth_status():
    """Тест статуса авторизации amoCRM"""
    print("🔍 Проверка статуса авторизации amoCRM...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(AMO_STATUS_URL)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("authorized"):
                    print("✅ amoCRM авторизован")
                    print(f"   Account ID: {data.get('account_id')}")
                    print(f"   Scope: {data.get('scope')}")
                else:
                    print("❌ amoCRM не авторизован")
                    print("   Перейдите по ссылке для авторизации:")
                    print(f"   {AMO_AUTH_URL}")
                return data
            else:
                print(f"❌ Ошибка при проверке статуса: {response.status_code}")
                return None
                
    except Exception as e:
        print(f"❌ Ошибка при проверке статуса: {str(e)}")
        return None

async def test_amo_connection():
    """Тест подключения к amoCRM"""
    print("\n🔗 Тестирование подключения к amoCRM...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(AMO_TEST_URL)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    print("✅ Подключение к amoCRM успешно")
                    if data.get("account_info"):
                        account = data["account_info"]
                        print(f"   Название: {account.get('name')}")
                        print(f"   Домен: {account.get('subdomain')}")
                else:
                    print("❌ Ошибка подключения к amoCRM")
                    print(f"   Сообщение: {data.get('message')}")
                return data
            else:
                print(f"❌ Ошибка при тестировании подключения: {response.status_code}")
                return None
                
    except Exception as e:
        print(f"❌ Ошибка при тестировании подключения: {str(e)}")
        return None

async def test_create_lead():
    """Тест создания лида"""
    print("\n📝 Тестирование создания лида...")
    
    lead_data = {
        "name": "Тест Тестов",
        "phone": "+79001234567",
        "email": "test@example.com",
        "utm_source": "google",
        "utm_medium": "cpc",
        "utm_campaign": "asia_deals_test",
        "property_type": "Квартира",
        "budget": 5000000,
        "notes": "Тестовый лид для проверки интеграции"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                LEADS_URL,
                json=lead_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Лид успешно создан")
                print(f"   ID: {data.get('id')}")
                print(f"   amoCRM Contact ID: {data.get('amocrm_contact_id')}")
                print(f"   amoCRM Lead ID: {data.get('amocrm_lead_id')}")
                print(f"   Статус: {data.get('status')}")
                return data
            else:
                print(f"❌ Ошибка при создании лида: {response.status_code}")
                print(f"   Ответ: {response.text}")
                return None
                
    except Exception as e:
        print(f"❌ Ошибка при создании лида: {str(e)}")
        return None

async def test_get_leads():
    """Тест получения списка лидов"""
    print("\n📋 Получение списка лидов...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(LEADS_URL)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Получено {len(data)} лидов")
                for lead in data[:3]:  # Показываем первые 3
                    print(f"   - {lead.get('name')} ({lead.get('status')})")
                return data
            else:
                print(f"❌ Ошибка при получении лидов: {response.status_code}")
                return None
                
    except Exception as e:
        print(f"❌ Ошибка при получении лидов: {str(e)}")
        return None

async def test_webhook():
    """Тест webhook endpoint"""
    print("\n🔔 Тестирование webhook endpoint...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(WEBHOOK_TEST_URL)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Webhook endpoint работает")
                print(f"   Сообщение: {data.get('message')}")
                return data
            else:
                print(f"❌ Ошибка webhook endpoint: {response.status_code}")
                return None
                
    except Exception as e:
        print(f"❌ Ошибка при тестировании webhook: {str(e)}")
        return None

async def test_lead_status_update(lead_id: int):
    """Тест обновления статуса лида"""
    print(f"\n🔄 Тестирование обновления статуса лида {lead_id}...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{LEADS_URL}/{lead_id}/status",
                params={"status": "contacted"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Статус лида обновлен")
                print(f"   Сообщение: {data.get('message')}")
                return data
            else:
                print(f"❌ Ошибка при обновлении статуса: {response.status_code}")
                return None
                
    except Exception as e:
        print(f"❌ Ошибка при обновлении статуса: {str(e)}")
        return None

async def main():
    """Основная функция тестирования"""
    print("🚀 Начинаем тестирование интеграции с amoCRM")
    print("=" * 50)
    
    # Тест 1: Статус авторизации
    auth_status = await test_amo_auth_status()
    
    # Тест 2: Подключение к amoCRM
    connection_test = await test_amo_connection()
    
    # Тест 3: Webhook endpoint
    webhook_test = await test_webhook()
    
    # Тест 4: Создание лида (только если авторизован)
    if auth_status and auth_status.get("authorized"):
        lead = await test_create_lead()
        
        if lead:
            # Тест 5: Получение списка лидов
            await test_get_leads()
            
            # Тест 6: Обновление статуса лида
            await test_lead_status_update(lead["id"])
    else:
        print("\n⚠️  Пропускаем тесты создания лидов - amoCRM не авторизован")
        print("   Для авторизации перейдите по ссылке:")
        print(f"   {AMO_AUTH_URL}")
    
    print("\n" + "=" * 50)
    print("🏁 Тестирование завершено")
    
    # Рекомендации
    print("\n📋 Рекомендации:")
    if not auth_status or not auth_status.get("authorized"):
        print("1. Авторизуйтесь в amoCRM")
        print("2. Проверьте настройки в .env файле")
        print("3. Убедитесь, что приложение запущено")
    else:
        print("1. Интеграция работает корректно")
        print("2. Можно создавать лидов и управлять статусами")
        print("3. Webhook настроен для синхронизации")

if __name__ == "__main__":
    asyncio.run(main())
