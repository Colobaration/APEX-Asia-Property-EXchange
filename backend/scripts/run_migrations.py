#!/usr/bin/env python3
"""
Скрипт для автоматического запуска миграций базы данных
Используется при старте приложения для обеспечения актуальности схемы БД
"""

import os
import sys
import time
import logging
from pathlib import Path

# Добавляем корневую папку backend в путь
backend_root = Path(__file__).parent.parent
sys.path.insert(0, str(backend_root))

from alembic.config import Config
from alembic import command
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def wait_for_database(db_url: str, max_retries: int = 30, retry_interval: int = 2):
    """
    Ожидание готовности базы данных
    """
    logger.info(f"Ожидание готовности базы данных: {db_url}")
    
    for attempt in range(max_retries):
        try:
            engine = create_engine(db_url)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("База данных готова!")
            return True
        except OperationalError as e:
            logger.warning(f"Попытка {attempt + 1}/{max_retries}: База данных недоступна: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_interval)
            else:
                logger.error("База данных не стала доступной в течение ожидаемого времени")
                return False
        except Exception as e:
            logger.error(f"Неожиданная ошибка при подключении к БД: {e}")
            return False

def run_migrations(alembic_cfg_path: str, db_url: str):
    """
    Запуск миграций Alembic
    """
    try:
        logger.info("Начинаем выполнение миграций...")
        
        # Создаем конфигурацию Alembic
        alembic_cfg = Config(alembic_cfg_path)
        alembic_cfg.set_main_option("sqlalchemy.url", db_url)
        
        # Проверяем текущую версию
        logger.info("Проверяем текущую версию миграций...")
        command.current(alembic_cfg)
        
        # Выполняем миграции
        logger.info("Выполняем миграции до последней версии...")
        command.upgrade(alembic_cfg, "head")
        
        logger.info("Миграции успешно выполнены!")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка при выполнении миграций: {e}")
        return False

def main():
    """
    Основная функция
    """
    # Получаем переменные окружения
    environment = os.getenv("ENVIRONMENT", "development")
    db_url = os.getenv("DATABASE_URL")
    
    if not db_url:
        logger.error("DATABASE_URL не установлена в переменных окружения")
        sys.exit(1)
    
    logger.info(f"Запуск миграций для окружения: {environment}")
    logger.info(f"База данных: {db_url}")
    
    # Путь к конфигурации Alembic
    alembic_cfg_path = backend_root / "alembic.ini"
    
    if not alembic_cfg_path.exists():
        logger.error(f"Файл конфигурации Alembic не найден: {alembic_cfg_path}")
        sys.exit(1)
    
    # Ждем готовности базы данных
    if not wait_for_database(db_url):
        logger.error("Не удалось дождаться готовности базы данных")
        sys.exit(1)
    
    # Запускаем миграции
    if not run_migrations(str(alembic_cfg_path), db_url):
        logger.error("Не удалось выполнить миграции")
        sys.exit(1)
    
    logger.info("Все миграции выполнены успешно!")

if __name__ == "__main__":
    main()
