"""
Сервис авторизации пользователей
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models import User


async def get_or_create_user(
    session: AsyncSession,
    telegram_id: int,
    username: str = None,
    full_name: str = None,
    phone: str = None
) -> User:
    """
    Получает пользователя из БД или создаёт нового
    
    Args:
        session: Сессия БД
        telegram_id: Telegram User ID
        username: Telegram username
        full_name: ФИО пользователя
        phone: Телефон
    
    Returns:
        User: Объект пользователя
    """
    # Пытаемся найти пользователя
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()
    
    if user:
        # Пользователь уже существует
        return user
    
    # Создаём нового пользователя
    user = User(
        telegram_id=telegram_id,
        username=username,
        full_name=full_name or "",
        phone=phone or "",
        consent_personal_data=False
    )
    
    session.add(user)
    await session.commit()
    await session.refresh(user)
    
    return user


async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int) -> User | None:
    """
    Получает пользователя по Telegram ID
    """
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    return result.scalar_one_or_none()


# ========================================
# Пример использования:
# ========================================
# from backend.services.auth import get_or_create_user
# 
# async with async_session() as session:
#     user = await get_or_create_user(
#         session,
#         telegram_id=123456789,
#         full_name="Иванова Мария"
#     )

