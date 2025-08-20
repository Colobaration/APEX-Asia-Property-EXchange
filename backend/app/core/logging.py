import logging
from loguru import logger
from app.core.config import settings

# Настройка логирования
def setup_logging():
    """Настройка системы логирования"""
    
    # Удаление стандартного обработчика
    logger.remove()
    
    # Добавление обработчика для консоли
    logger.add(
        "logs/app.log",
        rotation="10 MB",
        retention="30 days",
        level=settings.log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
        compression="zip"
    )
    
    # Добавление обработчика для ошибок
    logger.add(
        "logs/error.log",
        rotation="10 MB",
        retention="90 days",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
        compression="zip"
    )
    
    # Перехват стандартного logging
    class InterceptHandler(logging.Handler):
        def emit(self, record):
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno
            
            frame, depth = logging.currentframe(), 2
            while frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1
            
            logger.opt(depth=depth, exception=record.exc_info).log(
                level, record.getMessage()
            )
    
    # Настройка стандартного logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    
    return logger

# Инициализация логгера
setup_logging()
