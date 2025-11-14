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
# Глобальные переменные для engine и session
# ========================================
# КРИТИЧНО: engine и session создаются только в startup_event FastAPI
# Это гарантирует, что они создаются в правильном event loop
_engine: Optional[AsyncEngine] = None
_async_session: Optional[async_sessionmaker] = None


def create_engine_and_session():
    """
    Создать engine и session factory
    ДОЛЖНО вызываться только в startup_event FastAPI!
    """
    global _engine, _async_session
    
    print("🔧 Создание engine и session factory...")
    
    # КРИТИЧНО: Очищаем метаданные Base перед созданием engine
    # Это гарантирует, что SQLAlchemy перечитает структуру моделей
    # Очищаем ДО импорта моделей, чтобы они зарегистрировались заново
    Base.metadata.clear()
    # Теперь импортируем модели - они автоматически зарегистрируются в Base.metadata
    from backend.database.models import User, Course, Lesson, UserCourse, UserProgress, Achievement, UserAchievement, Community, Payment, Certificate, Favorite, Review, Challenge, UserChallenge, SupportTicket, SupportMessage
    
    # Параметры для разных типов БД
    db_url = settings.database_url
    is_sqlite = db_url.startswith("sqlite")
    
    if is_sqlite:
        # SQLite для локальной разработки
        _engine = create_async_engine(
            db_url,
            echo=settings.ENVIRONMENT == "development",
            future=True,
            connect_args={"check_same_thread": False}  # Для SQLite
        )
    else:
        # PostgreSQL для продакшена
        # Важно: statement_cache_size передается через connect_args для asyncpg
        # Это отключает кеширование prepared statements, что решает проблему
        # когда структура таблицы изменилась, но asyncpg использует закешированный statement
        _engine = create_async_engine(
            db_url,
            echo=settings.ENVIRONMENT == "development",
            future=True,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600,
            pool_reset_on_return='commit',  # Сбрасываем соединения при возврате в пул
            connect_args={
                "server_settings": {
                    "application_name": "beauty_school_api"
                },
                "statement_cache_size": 0  # Отключаем кеш prepared statements в asyncpg
            }
        )
    
    _async_session = async_sessionmaker(
        _engine,
        class_=AsyncSession,
        expire_on_commit=False,  # Объекты не истекают после commit
        autoflush=False,
        autocommit=False,
    )
    
    print("✅ Engine и session factory созданы")


def get_engine() -> AsyncEngine:
    """
    Получить engine БД
    Должен быть создан в startup_event перед использованием!
    """
    global _engine
    if _engine is None:
        raise RuntimeError("Engine не инициализирован! Вызовите create_engine_and_session() в startup_event")
    return _engine


def get_async_session() -> async_sessionmaker:
    """
    Получить фабрику сессий
    Должна быть создана в startup_event перед использованием!
    """
    global _async_session
    if _async_session is None:
        raise RuntimeError("Session factory не инициализирована! Вызовите create_engine_and_session() в startup_event")
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
        """Вызов async_session() возвращает сам объект для использования как async context manager"""
        # Возвращаем сам объект, который поддерживает async context manager
        return self
    
    def __getattr__(self, name):
        """Доступ к атрибутам фабрики сессий"""
        return getattr(get_async_session(), name)
    
    async def __aenter__(self):
        """Для async context manager - создаем session"""
        session_factory = get_async_session()
        self._session = session_factory()
        return await self._session.__aenter__()
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Для async context manager - закрываем session"""
        if hasattr(self, '_session'):
            return await self._session.__aexit__(exc_type, exc_val, exc_tb)

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

