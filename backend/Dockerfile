FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Копирование requirements и установка Python зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Создание пользователя для безопасности
RUN useradd --create-home --shell /bin/bash app

# Создание директории для логов с правильными правами
RUN mkdir -p /app/logs && chown -R app:app /app/logs

# Копирование кода приложения
COPY . .

# Делаем entrypoint скрипт исполняемым
RUN chmod +x docker-entrypoint.sh

# Устанавливаем правильные права на все файлы
RUN chown -R app:app /app

# Переключаемся на пользователя app
USER app

# Экспорт порта
EXPOSE 8000

# Используем entrypoint скрипт
ENTRYPOINT ["./docker-entrypoint.sh"]
