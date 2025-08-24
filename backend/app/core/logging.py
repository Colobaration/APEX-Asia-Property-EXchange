import logging
import logging.handlers
import sys
from pathlib import Path
from app.core.config import settings

def setup_logging():
    """Настройка логирования для приложения"""
    
    # Создаем директорию для логов если её нет
    log_dir = Path("logs")
    try:
        log_dir.mkdir(exist_ok=True)
    except PermissionError:
        # Если нет прав на создание директории, используем только консольное логирование
        print("⚠️  Предупреждение: Нет прав на создание директории логов. Используется только консольное логирование.")
    
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
        try:
            # Убираем 'logs/' из пути, если он уже есть
            log_file_path = settings.log_file
            if log_file_path.startswith('logs/'):
                log_file_path = log_file_path[6:]  # Убираем 'logs/'
            
            # Проверяем, можем ли мы создать файл
            log_file_full_path = log_dir / log_file_path
            
            # Пытаемся создать файл для проверки прав
            try:
                with open(log_file_full_path, 'a') as f:
                    pass
            except PermissionError:
                raise PermissionError(f"Нет прав на запись в файл: {log_file_full_path}")
            
            file_handler = logging.handlers.RotatingFileHandler(
                log_file_full_path,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
            print(f"✅ Файловое логирование настроено: {log_file_full_path}")
        except (PermissionError, OSError) as e:
            print(f"⚠️  Предупреждение: Не удалось настроить файловое логирование: {e}")
            print("📝 Используется только консольное логирование")
    
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
