#!/usr/bin/env python3
"""
Скрипт инициализации базы данных
Создает базу данных, выполняет миграции и добавляет начальные данные
"""

import os
import sys
import logging
from pathlib import Path

# Добавляем корневую папку backend в путь
backend_root = Path(__file__).parent.parent
sys.path.insert(0, str(backend_root))

from scripts.run_migrations import wait_for_database, run_migrations
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_database_if_not_exists(db_url: str):
    """
    Создает базу данных, если она не существует
    """
    try:
        # Извлекаем параметры подключения
        from urllib.parse import urlparse
        parsed = urlparse(db_url)
        
        # Создаем URL для подключения к postgres (без указания базы данных)
        postgres_url = f"postgresql://{parsed.username}:{parsed.password}@{parsed.hostname}:{parsed.port}/postgres"
        
        engine = create_engine(postgres_url)
        
        with engine.connect() as conn:
            # Проверяем, существует ли база данных
            result = conn.execute(text(
                "SELECT 1 FROM pg_database WHERE datname = :dbname"
            ), {"dbname": parsed.path[1:]})  # Убираем первый символ '/'
            
            if not result.fetchone():
                logger.info(f"Создаем базу данных: {parsed.path[1:]}")
                # Создаем базу данных
                conn.execute(text(f"CREATE DATABASE {parsed.path[1:]}"))
                conn.commit()
                logger.info("База данных создана успешно!")
            else:
                logger.info("База данных уже существует")
                
    except Exception as e:
        logger.error(f"Ошибка при создании базы данных: {e}")
        return False
    
    return True

def add_initial_data(db_url: str):
    """
    Добавляет начальные данные в базу
    """
    try:
        engine = create_engine(db_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        with SessionLocal() as session:
            # Здесь можно добавить начальные данные
            # Например, создание администратора, настройки по умолчанию и т.д.
            
            logger.info("Начальные данные добавлены успешно!")
            
    except Exception as e:
        logger.error(f"Ошибка при добавлении начальных данных: {e}")
        return False
    
    return True

def main():
    """
    Основная функция инициализации
    """
    # Получаем переменные окружения
    environment = os.getenv("ENVIRONMENT", "development")
    db_url = os.getenv("DATABASE_URL")
    
    if not db_url:
        logger.error("DATABASE_URL не установлена в переменных окружения")
        sys.exit(1)
    
    logger.info(f"Инициализация базы данных для окружения: {environment}")
    logger.info(f"База данных: {db_url}")
    
    # Путь к конфигурации Alembic
    alembic_cfg_path = backend_root / "alembic.ini"
    
    if not alembic_cfg_path.exists():
        logger.error(f"Файл конфигурации Alembic не найден: {alembic_cfg_path}")
        sys.exit(1)
    
    # 1. Создаем базу данных, если не существует
    logger.info("Шаг 1: Проверка/создание базы данных...")
    if not create_database_if_not_exists(db_url):
        logger.error("Не удалось создать базу данных")
        sys.exit(1)
    
    # 2. Ждем готовности базы данных
    logger.info("Шаг 2: Ожидание готовности базы данных...")
    if not wait_for_database(db_url):
        logger.error("Не удалось дождаться готовности базы данных")
        sys.exit(1)
    
    # 3. Запускаем миграции
    logger.info("Шаг 3: Выполнение миграций...")
    if not run_migrations(str(alembic_cfg_path), db_url):
        logger.error("Не удалось выполнить миграции")
        sys.exit(1)
    
    # 4. Добавляем начальные данные
    logger.info("Шаг 4: Добавление начальных данных...")
    if not add_initial_data(db_url):
        logger.warning("Не удалось добавить начальные данные")
    
    logger.info("Инициализация базы данных завершена успешно!")

if __name__ == "__main__":
    main()
