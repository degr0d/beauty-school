"""
Настройка логирования
"""

import logging
import sys
from pathlib import Path

from backend.config import settings


def setup_logger(name: str = "beauty_school") -> logging.Logger:
    """
    Настраивает и возвращает logger
    
    Args:
        name: Имя logger'а
    
    Returns:
        logging.Logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Формат логов
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (опционально)
    if settings.ENVIRONMENT == "production":
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        file_handler = logging.FileHandler(log_dir / "app.log")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


# Глобальный logger
logger = setup_logger()


# ========================================
# Использование в коде:
# ========================================
# from backend.utils.logger import logger
# 
# logger.info("Приложение запущено")
# logger.error("Ошибка подключения к БД")

