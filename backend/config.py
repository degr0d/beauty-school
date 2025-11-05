"""
Конфигурация приложения
Загружает переменные окружения из .env файла
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from dotenv import load_dotenv


class Settings(BaseSettings):
    """
    Настройки приложения, загружаются из .env файла
    """
    
    # ========================================
    # Telegram Bot
    # ========================================
    BOT_TOKEN: str
    ADMIN_BOT_TOKEN: str
    ADMIN_IDS: str  # Список через запятую, например: "123456789,987654321"
    
    @property
    def admin_ids_list(self) -> List[int]:
        """Преобразует строку ADMIN_IDS в список int"""
        return [int(id.strip()) for id in self.ADMIN_IDS.split(',') if id.strip()]
    
    # ========================================
    # Database
    # ========================================
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "beauty_db"
    DB_USER: str = "beauty_user"
    DB_PASSWORD: str
    
    @property
    def database_url(self) -> str:
        """Строка подключения к PostgreSQL (async)"""
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def database_url_sync(self) -> str:
        """Строка подключения к PostgreSQL (sync, для Alembic)"""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    # ========================================
    # Redis (опционально)
    # ========================================
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0
    
    @property
    def redis_url(self) -> str:
        """Строка подключения к Redis"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # ========================================
    # FastAPI
    # ========================================
    API_PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:5173"  # Vite dev сервер
    WEBAPP_URL: str = "http://localhost:5173"  # URL для Mini App (в продакшене будет https://yourdomain.com)
    BACKEND_URL: str = "http://localhost:8000"
    SECRET_KEY: str = "change_me_in_production"
    ENVIRONMENT: str = "development"  # development / production
    
    # ========================================
    # File Storage
    # ========================================
    LOCAL_STORAGE_PATH: str = "./uploads"
    
    # S3 (опционально)
    S3_ENDPOINT: str = ""
    S3_BUCKET: str = ""
    S3_ACCESS_KEY: str = ""
    S3_SECRET_KEY: str = ""
    S3_REGION: str = "us-east-1"
    
    # ========================================
    # Payment (ЮKassa)
    # ========================================
    YUKASSA_SHOP_ID: str = ""  # Получить в личном кабинете ЮKassa
    YUKASSA_SECRET_KEY: str = ""  # Получить в личном кабинете ЮKassa
    YUKASSA_RETURN_URL: str = ""  # URL для возврата после оплаты (например: https://yourdomain.com/payment/success)
    
    # ========================================
    # Logging
    # ========================================
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    
    # ========================================
    # Misc
    # ========================================
    TIMEZONE: str = "Europe/Moscow"
    DEFAULT_LANGUAGE: str = "ru"
    
    # Конфигурация загрузки из .env
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# Создаём глобальный экземпляр настроек
settings = Settings()


def reload_settings():
    """
    Перезагружает настройки из .env файла
    Полезно когда WEBAPP_URL обновляется туннелем
    
    Returns:
        Обновлённый объект settings
    """
    load_dotenv(override=True)  # Перезагружаем .env
    global settings
    settings = Settings()  # Пересоздаём объект настроек
    return settings


def get_webapp_url() -> str:
    """
    Получает актуальный WEBAPP_URL с автоматической перезагрузкой настроек
    Используйте эту функцию вместо прямого обращения к settings.WEBAPP_URL
    
    Если URL не HTTPS - возвращает fallback (localhost для разработки)
    """
    reload_settings()
    url = settings.WEBAPP_URL
    
    # Проверяем что URL начинается с https://
    if not url.startswith('https://'):
        # Если не HTTPS - возвращаем fallback или показываем предупреждение
        if url.startswith('http://localhost'):
            # Для локальной разработки без туннеля
            return url
        else:
            # Если установлен неправильный URL - используем localhost
            return "http://localhost:5173"
    
    return url


# ========================================
# Пример использования в других модулях:
# ========================================
# from backend.config import settings
# 
# bot_token = settings.BOT_TOKEN
# database_url = settings.database_url
# admin_ids = settings.admin_ids_list

