import re
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import hashlib
import secrets

def validate_phone(phone: str) -> bool:
    """Валидация номера телефона"""
    # Российский формат: +7XXXXXXXXXX
    pattern = r'^\+7\d{10}$'
    return bool(re.match(pattern, phone))

def validate_email(email: str) -> bool:
    """Валидация email адреса"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def extract_utm_params(url: str) -> Dict[str, str]:
    """Извлечение UTM параметров из URL"""
    utm_params = {}
    
    # Парсинг URL параметров
    if '?' in url:
        query_string = url.split('?')[1]
        params = query_string.split('&')
        
        for param in params:
            if '=' in param:
                key, value = param.split('=', 1)
                if key.startswith('utm_'):
                    utm_params[key] = value
    
    return utm_params

def calculate_cpl(total_cost: float, leads_count: int) -> float:
    """Расчет CPL (Cost Per Lead)"""
    if leads_count == 0:
        return 0.0
    return total_cost / leads_count

def calculate_conversion_rate(leads_count: int, deals_count: int) -> float:
    """Расчет Conversion Rate"""
    if leads_count == 0:
        return 0.0
    return (deals_count / leads_count) * 100

def calculate_roi(revenue: float, cost: float) -> float:
    """Расчет ROI (Return on Investment)"""
    if cost == 0:
        return 0.0
    return ((revenue - cost) / cost) * 100

def generate_secure_token(length: int = 32) -> str:
    """Генерация безопасного токена"""
    return secrets.token_urlsafe(length)

def hash_password(password: str) -> str:
    """Хеширование пароля"""
    return hashlib.sha256(password.encode()).hexdigest()

def format_currency(amount: float, currency: str = "USD") -> str:
    """Форматирование валюты"""
    if currency == "USD":
        return f"${amount:,.2f}"
    elif currency == "RUB":
        return f"{amount:,.2f} ₽"
    else:
        return f"{amount:,.2f} {currency}"

def get_date_range(period: str) -> tuple[datetime, datetime]:
    """Получение диапазона дат по периоду"""
    end_date = datetime.now()
    
    if period == "7d":
        start_date = end_date - timedelta(days=7)
    elif period == "30d":
        start_date = end_date - timedelta(days=30)
    elif period == "90d":
        start_date = end_date - timedelta(days=90)
    else:
        start_date = end_date - timedelta(days=30)
    
    return start_date, end_date

def sanitize_string(text: str) -> str:
    """Очистка строки от потенциально опасных символов"""
    # Удаление HTML тегов
    text = re.sub(r'<[^>]+>', '', text)
    
    # Удаление специальных символов
    text = re.sub(r'[<>"\']', '', text)
    
    return text.strip()

def parse_amocrm_custom_fields(custom_fields: list) -> Dict[str, Any]:
    """Парсинг кастомных полей amoCRM"""
    result = {}
    
    for field in custom_fields:
        field_id = field.get('field_id')
        values = field.get('values', [])
        
        if values:
            value = values[0].get('value')
            result[f'field_{field_id}'] = value
    
    return result

def build_amocrm_custom_fields(fields_data: Dict[str, Any]) -> list:
    """Сборка кастомных полей для amoCRM"""
    custom_fields = []
    
    for field_name, value in fields_data.items():
        if value is not None:
            # Извлечение ID поля из названия
            if field_name.startswith('field_'):
                field_id = int(field_name.split('_')[1])
                
                custom_fields.append({
                    "field_id": field_id,
                    "values": [{"value": str(value)}]
                })
    
    return custom_fields
