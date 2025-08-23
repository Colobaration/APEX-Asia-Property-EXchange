#!/usr/bin/env python3
"""
Скрипт для тестирования вебхук сервера AmoCRM
"""

import requests
import json
import hashlib
import hmac
import time
from datetime import datetime
from typing import Dict, Any

class WebhookTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client_uuid = "test-webhook-client"
        self.account_id = "test-account-123"
        self.client_secret = "test-secret-key"
    
    def generate_signature(self, client_uuid: str, account_id: str, client_secret: str) -> str:
        """Генерация HMAC подписи для webhook"""
        message = f"{client_uuid}|{account_id}"
        signature = hmac.new(
            client_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def test_health_endpoint(self) -> bool:
        """Тест health check endpoint"""
        print("🔍 Тестирование health check endpoint...")
        
        try:
            response = requests.get(f"{self.base_url}/api/webhooks/amo/health")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check успешен: {data}")
                return True
            else:
                print(f"❌ Health check неудачен: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка health check: {str(e)}")
            return False
    
    def test_webhook_test_endpoint(self) -> bool:
        """Тест тестового endpoint"""
        print("🔍 Тестирование webhook test endpoint...")
        
        try:
            response = requests.get(f"{self.base_url}/api/webhooks/amo/test")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Test endpoint успешен: {data}")
                return True
            else:
                print(f"❌ Test endpoint неудачен: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка test endpoint: {str(e)}")
            return False
    
    def test_webhook_with_valid_data(self) -> bool:
        """Тест webhook с валидными данными"""
        print("🔍 Тестирование webhook с валидными данными...")
        
        # Создаем тестовые данные
        webhook_data = {
            "leads": {
                "add": [
                    {
                        "id": 12345,
                        "name": "Тестовый лид",
                        "status_id": 1,
                        "created_at": int(time.time()),
                        "custom_fields_values": [
                            {
                                "field_id": 123458,
                                "values": [{"value": "google"}]
                            },
                            {
                                "field_id": 123459,
                                "values": [{"value": "cpc"}]
                            }
                        ]
                    }
                ],
                "update": [],
                "delete": []
            },
            "contacts": {
                "add": [
                    {
                        "id": 67890,
                        "name": "Тестовый контакт",
                        "custom_fields_values": [
                            {
                                "field_id": 123456,
                                "values": [{"value": "+79001234567"}]
                            },
                            {
                                "field_id": 123457,
                                "values": [{"value": "test@example.com"}]
                            }
                        ]
                    }
                ],
                "update": []
            }
        }
        
        # Генерируем подпись
        signature = self.generate_signature(
            self.client_uuid, self.account_id, self.client_secret
        )
        
        headers = {
            "Content-Type": "application/json",
            "X-Client-UUID": self.client_uuid,
            "X-Signature": signature,
            "X-Account-ID": self.account_id
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/webhooks/amo",
                json=webhook_data,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Webhook успешно обработан: {data}")
                return True
            else:
                print(f"❌ Webhook неудачен: {response.status_code}")
                print(f"Ответ: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка webhook: {str(e)}")
            return False
    
    def test_webhook_with_invalid_signature(self) -> bool:
        """Тест webhook с невалидной подписью"""
        print("🔍 Тестирование webhook с невалидной подписью...")
        
        webhook_data = {
            "leads": {
                "add": [{"id": 12345, "name": "Тест"}]
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "X-Client-UUID": self.client_uuid,
            "X-Signature": "invalid-signature",
            "X-Account-ID": self.account_id
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/webhooks/amo",
                json=webhook_data,
                headers=headers
            )
            
            if response.status_code == 401:
                print("✅ Невалидная подпись правильно отклонена")
                return True
            else:
                print(f"❌ Неожиданный статус: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка теста: {str(e)}")
            return False
    
    def test_webhook_with_invalid_data(self) -> bool:
        """Тест webhook с невалидными данными"""
        print("🔍 Тестирование webhook с невалидными данными...")
        
        # Невалидные данные
        webhook_data = {
            "invalid": "data",
            "leads": {
                "add": "not-a-list"  # Должен быть список
            }
        }
        
        signature = self.generate_signature(
            self.client_uuid, self.account_id, self.client_secret
        )
        
        headers = {
            "Content-Type": "application/json",
            "X-Client-UUID": self.client_uuid,
            "X-Signature": signature,
            "X-Account-ID": self.account_id
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/webhooks/amo",
                json=webhook_data,
                headers=headers
            )
            
            if response.status_code == 400:
                print("✅ Невалидные данные правильно отклонены")
                return True
            else:
                print(f"❌ Неожиданный статус: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка теста: {str(e)}")
            return False
    
    def test_lead_status_update(self) -> bool:
        """Тест обновления статуса лида"""
        print("🔍 Тестирование обновления статуса лида...")
        
        webhook_data = {
            "leads": {
                "update": [
                    {
                        "id": 12345,
                        "name": "Обновленный лид",
                        "status_id": 3,  # Презентация
                        "custom_fields_values": [
                            {
                                "field_id": 123463,
                                "values": [{"value": "500000"}]
                            }
                        ]
                    }
                ]
            }
        }
        
        signature = self.generate_signature(
            self.client_uuid, self.account_id, self.client_secret
        )
        
        headers = {
            "Content-Type": "application/json",
            "X-Client-UUID": self.client_uuid,
            "X-Signature": signature,
            "X-Account-ID": self.account_id
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/webhooks/amo",
                json=webhook_data,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Обновление статуса успешно: {data}")
                return True
            else:
                print(f"❌ Обновление статуса неудачно: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка обновления статуса: {str(e)}")
            return False
    
    def test_contact_update(self) -> bool:
        """Тест обновления контакта"""
        print("🔍 Тестирование обновления контакта...")
        
        webhook_data = {
            "contacts": {
                "update": [
                    {
                        "id": 67890,
                        "name": "Обновленный контакт",
                        "custom_fields_values": [
                            {
                                "field_id": 123456,
                                "values": [{"value": "+79009876543"}]
                            },
                            {
                                "field_id": 123457,
                                "values": [{"value": "updated@example.com"}]
                            }
                        ]
                    }
                ]
            }
        }
        
        signature = self.generate_signature(
            self.client_uuid, self.account_id, self.client_secret
        )
        
        headers = {
            "Content-Type": "application/json",
            "X-Client-UUID": self.client_uuid,
            "X-Signature": signature,
            "X-Account-ID": self.account_id
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/webhooks/amo",
                json=webhook_data,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Обновление контакта успешно: {data}")
                return True
            else:
                print(f"❌ Обновление контакта неудачно: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка обновления контакта: {str(e)}")
            return False
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Запуск всех тестов"""
        print("🚀 Запуск тестов вебхук сервера AmoCRM")
        print("=" * 50)
        
        tests = {
            "health_check": self.test_health_endpoint,
            "test_endpoint": self.test_webhook_test_endpoint,
            "valid_webhook": self.test_webhook_with_valid_data,
            "invalid_signature": self.test_webhook_with_invalid_signature,
            "invalid_data": self.test_webhook_with_invalid_data,
            "lead_status_update": self.test_lead_status_update,
            "contact_update": self.test_contact_update
        }
        
        results = {}
        
        for test_name, test_func in tests.items():
            print(f"\n📋 Тест: {test_name}")
            print("-" * 30)
            
            try:
                result = test_func()
                results[test_name] = result
                
                if result:
                    print(f"✅ {test_name}: ПРОЙДЕН")
                else:
                    print(f"❌ {test_name}: ПРОВАЛЕН")
                    
            except Exception as e:
                print(f"❌ {test_name}: ОШИБКА - {str(e)}")
                results[test_name] = False
        
        # Итоговый отчет
        print("\n" + "=" * 50)
        print("📊 ИТОГОВЫЙ ОТЧЕТ")
        print("=" * 50)
        
        passed = sum(results.values())
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ ПРОЙДЕН" if result else "❌ ПРОВАЛЕН"
            print(f"{test_name}: {status}")
        
        print(f"\nВсего тестов: {total}")
        print(f"Пройдено: {passed}")
        print(f"Провалено: {total - passed}")
        print(f"Процент успеха: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n🎉 Все тесты пройдены успешно!")
        else:
            print(f"\n⚠️  {total - passed} тестов провалено")
        
        return results

def main():
    """Основная функция"""
    import sys
    
    # Парсим аргументы командной строки
    base_url = "http://localhost:8000"
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    print(f"🎯 Тестирование вебхук сервера по адресу: {base_url}")
    
    # Создаем тестер и запускаем тесты
    tester = WebhookTester(base_url)
    results = tester.run_all_tests()
    
    # Возвращаем код выхода
    if all(results.values()):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
