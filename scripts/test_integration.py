#!/usr/bin/env python3
"""
Тестовый скрипт для проверки интеграции с amoCRM
"""

import asyncio
import httpx
import json
from typing import Dict, Any

class IntegrationTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def test_connection(self) -> bool:
        """Тест подключения к API"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            if response.status_code == 200:
                print("✅ API доступен")
                return True
            else:
                print(f"❌ API недоступен: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Ошибка подключения: {str(e)}")
            return False
    
    async def test_amo_auth_status(self) -> bool:
        """Тест статуса авторизации amoCRM"""
        try:
            response = await self.client.get(f"{self.base_url}/api/auth/amo/status")
            print(f"📊 Статус авторизации amoCRM: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Данные: {data}")
                return True
            return False
        except Exception as e:
            print(f"❌ Ошибка проверки авторизации: {str(e)}")
            return False
    
    async def test_create_lead(self) -> bool:
        """Тест создания лида"""
        try:
            lead_data = {
                "name": "Тест Тестов",
                "phone": "+79001234567",
                "email": "test@example.com",
                "utm_source": "google",
                "utm_medium": "cpc",
                "utm_campaign": "asia_deals_test",
                "utm_content": "banner_1",
                "utm_term": "недвижимость азии"
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/leads/",
                json=lead_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"📝 Создание лида: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Создан лид ID: {data.get('id')}")
                print(f"   amoCRM Contact ID: {data.get('amocrm_contact_id')}")
                print(f"   amoCRM Lead ID: {data.get('amocrm_lead_id')}")
                return True
            else:
                print(f"   Ошибка: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка создания лида: {str(e)}")
            return False
    
    async def test_webhook(self) -> bool:
        """Тест webhook обработчика"""
        try:
            webhook_data = {
                "leads": {
                    "add": [
                        {
                            "id": 123,
                            "name": "Тестовая сделка",
                            "status_id": 1,
                            "price": 50000
                        }
                    ]
                },
                "contacts": {
                    "add": [
                        {
                            "id": 456,
                            "name": "Тестовый контакт",
                            "phone": "+79001234567"
                        }
                    ]
                }
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/webhooks/amo",
                json=webhook_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"🔗 Webhook обработка: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Результат: {data}")
                return True
            else:
                print(f"   Ошибка: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка webhook: {str(e)}")
            return False
    
    async def test_analytics(self) -> bool:
        """Тест аналитических endpoints"""
        try:
            # Тест CPL
            response = await self.client.get(
                f"{self.base_url}/api/analytics/cpl",
                params={
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-31",
                    "utm_source": "google"
                }
            )
            
            print(f"📈 Аналитика CPL: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   CPL: {data.get('value', 'N/A')}")
                return True
            else:
                print(f"   Ошибка: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка аналитики: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """Запуск всех тестов"""
        print("🚀 Запуск тестов интеграции с amoCRM")
        print("=" * 50)
        
        tests = [
            ("Подключение к API", self.test_connection),
            ("Статус авторизации amoCRM", self.test_amo_auth_status),
            ("Создание лида", self.test_create_lead),
            ("Обработка webhook", self.test_webhook),
            ("Аналитика", self.test_analytics),
        ]
        
        results = []
        
        for test_name, test_func in tests:
            print(f"\n🧪 {test_name}:")
            try:
                result = await test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ Ошибка выполнения теста: {str(e)}")
                results.append((test_name, False))
        
        # Итоговый отчет
        print("\n" + "=" * 50)
        print("📊 ИТОГОВЫЙ ОТЧЕТ:")
        print("=" * 50)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results:
            status = "✅ ПРОЙДЕН" if result else "❌ ПРОВАЛЕН"
            print(f"{status} - {test_name}")
            if result:
                passed += 1
        
        print(f"\n📈 Результат: {passed}/{total} тестов пройдено")
        
        if passed == total:
            print("🎉 Все тесты пройдены! Интеграция работает корректно.")
        else:
            print("⚠️  Некоторые тесты не пройдены. Проверьте настройки.")
        
        await self.client.aclose()

async def main():
    """Главная функция"""
    tester = IntegrationTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
