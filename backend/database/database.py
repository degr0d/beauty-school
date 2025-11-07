"""
Подключение к базе данных PostgreSQL
Использует SQLAlchemy 2.0 с async поддержкой
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, AsyncEngine
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator, Optional
import asyncio

from backend.config import settings


# ========================================
# Ленивая инициализация движка БД
# ========================================
# Проблема: engine создавался при импорте модуля, до создания event loop FastAPI
# Решение: создаем engine лениво, только когда он нужен
_engine: Optional[AsyncEngine] = None
_async_session: Optional[async_sessionmaker] = None
_lock = asyncio.Lock()


def get_engine() -> AsyncEngine:
    """
    Получить или создать engine БД
    Создается лениво, только когда нужен
    """
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            settings.database_url,
            echo=settings.ENVIRONMENT == "development",  # Логирование SQL-запросов в dev-режиме
            future=True,
            pool_size=10,  # Размер пула соединений
            max_overflow=20,  # Максимум дополнительных соединений
            pool_pre_ping=True,  # Проверка соединений перед использованием
            pool_recycle=3600,  # Пересоздание соединений каждый час
            connect_args={
                "server_settings": {
                    "application_name": "beauty_school_api"
                }
            }
        )
    return _engine


def get_async_session() -> async_sessionmaker:
    """
    Получить или создать фабрику сессий
    Создается лениво, только когда нужна
    """
    global _async_session
    if _async_session is None:
        _async_session = async_sessionmaker(
            get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,  # Объекты не истекают после commit
            autoflush=False,
            autocommit=False,
        )
    return _async_session


# Для обратной совместимости - создаем классы-обертки
class LazyEngine:
    """Обертка для ленивой инициализации engine"""
    def __call__(self):
        return get_engine()
    
    def __getattr__(self, name):
        return getattr(get_engine(), name)

class LazyAsyncSession:
    """Обертка для ленивой инициализации async_session"""
    def __call__(self):
        """Вызов async_session() возвращает фабрику сессий (async_sessionmaker)"""
        # Возвращаем фабрику сессий, которую можно использовать с async with
        return get_async_session()
    
    def __getattr__(self, name):
        """Доступ к атрибутам фабрики сессий"""
        return getattr(get_async_session(), name)

# Создаем экземпляры для обратной совместимости
engine = LazyEngine()
async_session = LazyAsyncSession()


# ========================================
# Base класс для моделей
# ========================================
Base = declarative_base()


# ========================================
# Dependency для FastAPI (получение сессии)
# ========================================
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency для FastAPI эндпоинтов
    
    Использование:
    @app.get("/users")
    async def get_users(session: AsyncSession = Depends(get_session)):
        ...
    """
    # Получаем фабрику сессий (создается лениво)
    session_factory = get_async_session()
    # Используем async with для правильного управления session
    # Это гарантирует, что session создается и закрывается в правильном event loop
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ========================================
# Инициализация БД (создание таблиц)
# ========================================
async def init_db():
    """
    Создаёт все таблицы в БД (для разработки)
    В продакшене используйте Alembic миграции!
    """
    from backend.database.models import (
        User, Course, Lesson, UserCourse, UserProgress,
        Achievement, UserAchievement, Community
    )
    
    # Получаем engine (создается лениво)
    db_engine = get_engine()
    async with db_engine.begin() as conn:
        # Раскомментируйте для пересоздания таблиц (ОСТОРОЖНО: удаляет данные!)
        # await conn.run_sync(Base.metadata.drop_all)
        
        await conn.run_sync(Base.metadata.create_all)


# ========================================
# Закрытие соединений (при остановке приложения)
# ========================================
async def close_db():
    """
    Закрывает все соединения с БД
    """
    global _engine
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _async_session = None


# ========================================
# Пример использования в коде:
# ========================================
# from backend.database import async_session
# from backend.database.models import User
# 
# async def create_user(telegram_id: int, full_name: str):
#     async with async_session() as session:
#         user = User(telegram_id=telegram_id, full_name=full_name)
#         session.add(user)
#         await session.commit()
#         await session.refresh(user)
#         return user

