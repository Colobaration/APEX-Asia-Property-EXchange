#!/usr/bin/env python3
"""
Скрипт для создания новых миграций Alembic
Используется для создания миграций при изменении моделей
"""

import os
import sys
import argparse
from pathlib import Path

# Добавляем корневую папку backend в путь
backend_root = Path(__file__).parent.parent
sys.path.insert(0, str(backend_root))

from alembic.config import Config
from alembic import command

def create_migration(message: str, alembic_cfg_path: str):
    """
    Создает новую миграцию Alembic
    """
    try:
        print(f"Создание миграции: {message}")
        
        # Создаем конфигурацию Alembic
        alembic_cfg = Config(alembic_cfg_path)
        
        # Создаем миграцию
        command.revision(alembic_cfg, message=message, autogenerate=True)
        
        print("✅ Миграция создана успешно!")
        print("📝 Не забудьте проверить и отредактировать созданный файл миграции")
        
    except Exception as e:
        print(f"❌ Ошибка при создании миграции: {e}")
        return False
    
    return True

def main():
    """
    Основная функция
    """
    parser = argparse.ArgumentParser(description="Создание новой миграции Alembic")
    parser.add_argument("message", help="Сообщение для миграции")
    parser.add_argument("--config", default="alembic.ini", help="Путь к конфигурации Alembic")
    
    args = parser.parse_args()
    
    # Путь к конфигурации Alembic
    alembic_cfg_path = backend_root / args.config
    
    if not alembic_cfg_path.exists():
        print(f"❌ Файл конфигурации Alembic не найден: {alembic_cfg_path}")
        sys.exit(1)
    
    # Создаем миграцию
    if not create_migration(args.message, str(alembic_cfg_path)):
        sys.exit(1)

if __name__ == "__main__":
    main()
