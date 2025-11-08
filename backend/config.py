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
    BOT_TOKEN: str = ""  # Опционально для API сервиса
    ADMIN_BOT_TOKEN: str = ""  # Опционально для API сервиса
    ADMIN_IDS: str = ""  # Список через запятую, например: "123456789,987654321"
    
    @property
    def admin_ids_list(self) -> List[int]:
        """Преобразует строку ADMIN_IDS в список int"""
        if not self.ADMIN_IDS:
            return []
        return [int(id.strip()) for id in self.ADMIN_IDS.split(',') if id.strip()]
    
    # ========================================
    # Database
    # ========================================
    # Railway автоматически предоставляет DATABASE_URL
    DATABASE_URL: str = ""  # Если установлен - используется напрямую
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "beauty_db"
    DB_USER: str = "postgres"  # По умолчанию для Docker
    DB_PASSWORD: str = "2580"  # По умолчанию для Docker (из docker-compose.yml)
    
    @property
    def database_url(self) -> str:
        """Строка подключения к БД (async)"""
        # Если Railway предоставил DATABASE_URL - используем его
        if self.DATABASE_URL and not self.DATABASE_URL.startswith("${"):
            # Конвертируем postgresql:// в postgresql+asyncpg://
            if self.DATABASE_URL.startswith("postgresql://"):
                return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
            return self.DATABASE_URL
        
        # Используем отдельные параметры PostgreSQL
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def database_url_sync(self) -> str:
        """Строка подключения к PostgreSQL (sync, для Alembic)"""
        # Если Railway предоставил DATABASE_URL - используем его как есть (уже postgresql://)
        if self.DATABASE_URL:
            return self.DATABASE_URL
        
        # Иначе используем отдельные параметры
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
    PORT: int = 8000  # Railway использует PORT переменную
    FRONTEND_URL: str = "http://localhost:5173"  # Vite dev сервер
    WEBAPP_URL: str = "http://localhost:5173"  # URL для Mini App (в продакшене будет https://yourdomain.com)
    BACKEND_URL: str = "http://localhost:8000"
    SECRET_KEY: str = "change_me_in_production"
    ENVIRONMENT: str = "development"  # development / production
    DEV_MODE: bool = True  # Режим разработки - позволяет работать без Telegram initData
    DEV_TELEGRAM_ID: int = 310836227  # Telegram ID для локальной разработки (админ по умолчанию)
    
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

