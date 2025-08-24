import logging
import logging.handlers
import sys
from pathlib import Path
from app.core.config import settings

def setup_logging():
    """Настройка логирования для приложения"""
    
    # Создаем директорию для логов если её нет
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Настраиваем форматтер
    formatter = logging.Formatter(
        fmt=settings.log_format,
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Настраиваем уровень логирования
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    
    # Настраиваем корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Очищаем существующие обработчики
    root_logger.handlers.clear()
    
    # Консольный обработчик
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Файловый обработчик (если указан файл логов)
    if settings.log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_dir / settings.log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Настраиваем логи для внешних библиотек
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("alembic").setLevel(logging.INFO)
    
    # Логируем информацию о настройке
    logger = logging.getLogger(__name__)
    logger.info(f"Логирование настроено. Уровень: {settings.log_level}")
    logger.info(f"Окружение: {settings.environment}")
    logger.info(f"Debug режим: {settings.debug}")

def get_logger(name: str) -> logging.Logger:
    """Получить логгер с указанным именем"""
    return logging.getLogger(name)

# Создаем глобальный логгер для импорта
logger = logging.getLogger(__name__)
