"""
Подключение к базе данных PostgreSQL
Использует SQLAlchemy 2.0 с async поддержкой
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator

from backend.config import settings


# ========================================
# Создание движка БД
# ========================================
engine = create_async_engine(
    settings.database_url,
    echo=settings.ENVIRONMENT == "development",  # Логирование SQL-запросов в dev-режиме
    future=True,
    pool_size=10,  # Размер пула соединений
    max_overflow=20,  # Максимум дополнительных соединений
)


# ========================================
# Фабрика сессий
# ========================================
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Объекты не истекают после commit
    autoflush=False,
    autocommit=False,
)


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
    # Создаем session через async_sessionmaker
    # Важно: не используем async with, чтобы избежать конфликтов с event loop
    session = async_session()
    try:
        # Убеждаемся, что session готов к использованию
        yield session
        # Коммитим только если не было исключений
        try:
            await session.commit()
        except Exception as commit_error:
            await session.rollback()
            raise commit_error
    except Exception as e:
        # Откатываем при любой ошибке
        try:
            await session.rollback()
        except Exception:
            pass  # Игнорируем ошибки при rollback
        raise e
    finally:
        # Закрываем session
        try:
            await session.close()
        except Exception:
            pass  # Игнорируем ошибки при close


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
    
    async with engine.begin() as conn:
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
    await engine.dispose()


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

