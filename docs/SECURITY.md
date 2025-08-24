# Документация по безопасности APEX

## Обзор

APEX реализует многоуровневую систему безопасности для защиты от различных типов атак и обеспечения целостности данных.

## Архитектура безопасности

### 1. Аутентификация и авторизация

#### JWT токены
- **Алгоритм**: HS256
- **Время жизни**: Настраивается в конфигурации
- **Хранение**: В заголовке Authorization: Bearer {token}
- **Обновление**: Автоматическое при каждом запросе

```python
# Создание токена
token = SecurityUtils.create_access_token({"sub": user_id, "email": user.email})

# Проверка токена
payload = SecurityUtils.verify_token(token)
```

#### Хеширование паролей
- **Алгоритм**: bcrypt
- **Соль**: Автоматическая
- **Раунды**: 12 (настраивается)

```python
# Хеширование пароля
hashed = SecurityUtils.get_password_hash(password)

# Проверка пароля
is_valid = SecurityUtils.verify_password(password, hashed)
```

### 2. Rate Limiting

#### Конфигурация
- **Лимит по умолчанию**: 100 запросов в час
- **Окно**: 3600 секунд (1 час)
- **Применяется к**: Все API endpoints

#### Настройка
```python
# Проверка rate limit
await check_rate_limit(request, limit=100, window=3600)
```

### 3. Webhook Security

#### Подписи HMAC
- **Алгоритм**: HMAC-SHA256
- **Секрет**: Настраивается в конфигурации
- **Заголовок**: X-Webhook-Signature

```python
# Проверка подписи
is_valid = SecurityUtils.verify_webhook_signature(
    payload, signature, secret
)
```

### 4. Idempotency

#### Ключи идемпотентности
- **Заголовок**: Idempotency-Key
- **Хранение**: В памяти (в продакшене - Redis)
- **Время жизни**: 24 часа

```python
# Генерация ключа
key = SecurityUtils.generate_idempotency_key()
```

### 5. Retry Logic

#### Exponential Backoff
- **Базовая задержка**: 1 секунда
- **Максимальная задержка**: 60 секунд
- **Jitter**: Да (для предотвращения thundering herd)

```python
@retry(max_attempts=3, base_delay=1.0, max_delay=60.0)
async def external_api_call():
    # API call logic
    pass
```

### 6. Circuit Breaker

#### Состояния
- **CLOSED**: Нормальная работа
- **OPEN**: Блокировка запросов
- **HALF_OPEN**: Тестовые запросы

```python
circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=60.0
)
result = await circuit_breaker.call(external_api_call)
```

## Middleware

### SecurityMiddleware
Добавляет security headers:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- `Content-Security-Policy` (в продакшене)

### LoggingMiddleware
- Логирует все запросы с уникальными ID
- Отслеживает время выполнения
- Логирует ошибки

### IdempotencyMiddleware
- Проверяет ключи идемпотентности
- Кэширует ответы для дублирующихся запросов

### WebhookSignatureMiddleware
- Проверяет подписи webhook'ов
- Блокирует запросы без подписи

## Frontend Security

### Protected Routes
```typescript
<ProtectedRoute requiredPermissions={['admin']}>
  <AdminPanel />
</ProtectedRoute>
```

### Authentication Hook
```typescript
const { user, isAuthenticated, login, logout } = useAuth();
```

### Error Boundary
```typescript
<ErrorBoundary onError={handleError}>
  <App />
</ErrorBoundary>
```

## Валидация данных

### Backend (Pydantic)
```python
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = Field(None, min_length=2)
```

### Frontend (Zod)
```typescript
const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});
```

## Мониторинг безопасности

### Логирование
- Все аутентификационные события
- Попытки доступа к защищенным ресурсам
- Rate limit превышения
- Webhook подписи

### Метрики
- Количество неудачных попыток входа
- Rate limit блокировки
- Время ответа API
- Ошибки валидации

## Best Practices

### 1. Пароли
- Минимум 8 символов
- Содержат буквы и цифры
- Не хранятся в открытом виде

### 2. API ключи
- Генерируются криптографически безопасно
- Хранятся в хешированном виде
- Регулярно ротируются

### 3. Webhook'и
- Всегда проверяйте подписи
- Используйте HTTPS
- Ограничивайте IP адреса

### 4. Rate Limiting
- Настройте лимиты для каждого endpoint
- Используйте разные лимиты для разных пользователей
- Мониторьте превышения

### 5. Retry Logic
- Используйте exponential backoff
- Добавляйте jitter
- Ограничивайте количество попыток

## Конфигурация

### Environment Variables
```bash
# JWT
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# Rate Limiting
RATE_LIMIT_DEFAULT=100
RATE_LIMIT_WINDOW=3600

# Webhook
AMOCRM_WEBHOOK_SECRET=your-webhook-secret

# CORS
CORS_ORIGINS=["http://localhost:3000", "https://yourdomain.com"]
ALLOWED_HOSTS=["localhost", "yourdomain.com"]
```

## Тестирование безопасности

### Unit Tests
```bash
# Запуск тестов безопасности
pytest tests/test_security.py -v
```

### Security Headers Test
```bash
# Проверка security headers
curl -I https://your-api.com/health
```

### Rate Limit Test
```bash
# Тест rate limiting
for i in {1..110}; do
  curl -X GET https://your-api.com/api/leads
done
```

## Incident Response

### 1. Обнаружение
- Мониторинг логов
- Алерты при подозрительной активности
- Автоматические блокировки

### 2. Анализ
- Логирование всех событий
- Сохранение контекста
- Определение источника

### 3. Реагирование
- Блокировка подозрительных IP
- Отзыв скомпрометированных токенов
- Уведомление администраторов

### 4. Восстановление
- Сброс паролей
- Обновление ключей
- Патч уязвимостей

## Обновления безопасности

### Регулярные обновления
- Зависимости обновляются еженедельно
- Security patches применяются немедленно
- Мониторинг CVE

### Dependency Scanning
```bash
# Проверка уязвимостей
pip-audit
npm audit
```

## Контакты

Для вопросов по безопасности:
- Email: security@apex.com
- PGP Key: [ссылка на ключ]
- Bug Bounty: [ссылка на программу]
