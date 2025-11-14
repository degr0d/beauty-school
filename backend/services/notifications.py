"""
Сервис для отправки пуш-уведомлений через Telegram бота
"""

import logging
from typing import Optional
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.config import settings
from backend.database import User

logger = logging.getLogger(__name__)

# Глобальный экземпляр бота для уведомлений
_notification_bot: Optional[Bot] = None


def get_notification_bot() -> Optional[Bot]:
    """
    Получить экземпляр бота для отправки уведомлений
    Создается лениво при первом использовании
    """
    global _notification_bot
    
    if _notification_bot is None and settings.BOT_TOKEN:
        try:
            _notification_bot = Bot(token=settings.BOT_TOKEN)
            logger.info("✅ Notification bot initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize notification bot: {e}")
            return None
    
    return _notification_bot


async def send_notification(
    telegram_id: int,
    message: str,
    parse_mode: Optional[str] = "HTML"
) -> bool:
    """
    Отправить уведомление пользователю
    
    Args:
        telegram_id: Telegram ID пользователя
        message: Текст сообщения
        parse_mode: Режим парсинга (HTML, Markdown, None)
    
    Returns:
        True если уведомление отправлено успешно, False в противном случае
    """
    bot = get_notification_bot()
    
    if not bot:
        logger.warning("Notification bot not available, skipping notification")
        return False
    
    try:
        await bot.send_message(
            chat_id=telegram_id,
            text=message,
            parse_mode=parse_mode
        )
        logger.info(f"✅ Notification sent to user {telegram_id}")
        return True
    except TelegramForbiddenError:
        # Пользователь заблокировал бота
        logger.warning(f"⚠️ User {telegram_id} blocked the bot")
        return False
    except TelegramBadRequest as e:
        logger.error(f"❌ Failed to send notification to {telegram_id}: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error sending notification to {telegram_id}: {e}")
        return False


async def send_achievement_notification(
    telegram_id: int,
    achievement_title: str,
    achievement_description: str,
    points: int
) -> bool:
    """
    Отправить уведомление о получении достижения
    
    Args:
        telegram_id: Telegram ID пользователя
        achievement_title: Название достижения
        achievement_description: Описание достижения
        points: Баллы за достижение
    
    Returns:
        True если уведомление отправлено успешно
    """
    message = (
        f"🎉 <b>Новое достижение!</b>\n\n"
        f"🏆 <b>{achievement_title}</b>\n"
        f"{achievement_description}\n\n"
        f"💎 +{points} баллов"
    )
    
    return await send_notification(telegram_id, message)


async def send_course_completed_notification(
    telegram_id: int,
    course_title: str,
    points_earned: int
) -> bool:
    """
    Отправить уведомление о завершении курса
    
    Args:
        telegram_id: Telegram ID пользователя
        course_title: Название курса
        points_earned: Баллы за завершение курса
    
    Returns:
        True если уведомление отправлено успешно
    """
    message = (
        f"🎓 <b>Поздравляем!</b>\n\n"
        f"Вы успешно завершили курс:\n"
        f"<b>{course_title}</b>\n\n"
        f"💎 +{points_earned} баллов\n\n"
        f"📜 Сертификат доступен в вашем профиле!"
    )
    
    return await send_notification(telegram_id, message)


async def send_next_course_recommendation(
    telegram_id: int,
    recommended_course_title: str,
    course_id: int
) -> bool:
    """
    Отправить уведомление с рекомендацией следующего курса
    
    Args:
        telegram_id: Telegram ID пользователя
        recommended_course_title: Название рекомендуемого курса
        course_id: ID рекомендуемого курса
    
    Returns:
        True если уведомление отправлено успешно
    """
    message = (
        f"📚 <b>Рекомендуем следующий курс!</b>\n\n"
        f"<b>{recommended_course_title}</b>\n\n"
        f"Продолжайте обучение и развивайте свои навыки! 💪"
    )
    
    return await send_notification(telegram_id, message)


async def send_community_recommendation(
    telegram_id: int,
    community_title: str,
    community_link: str,
    reason: str = ""
) -> bool:
    """
    Отправить уведомление с рекомендацией сообщества (чата)
    
    Args:
        telegram_id: Telegram ID пользователя
        community_title: Название сообщества
        community_link: Ссылка на Telegram-чат
        reason: Причина рекомендации (опционально)
    
    Returns:
        True если уведомление отправлено успешно
    """
    reason_text = f"\n{reason}\n" if reason else "\n"
    message = (
        f"💬 <b>Присоединяйтесь к сообществу!</b>\n\n"
        f"<b>{community_title}</b>{reason_text}"
        f"Общайтесь с единомышленниками и делитесь опытом! 👥"
    )
    
    # Если есть ссылка, добавляем её в сообщение
    if community_link:
        message += f"\n\n🔗 {community_link}"
    
    return await send_notification(telegram_id, message)


async def send_lesson_completed_notification(
    telegram_id: int,
    lesson_title: str,
    course_title: str,
    points_earned: int
) -> bool:
    """
    Отправить уведомление о завершении урока
    
    Args:
        telegram_id: Telegram ID пользователя
        lesson_title: Название урока
        course_title: Название курса
        points_earned: Баллы за урок
    
    Returns:
        True если уведомление отправлено успешно
    """
    message = (
        f"✅ Урок завершен!\n\n"
        f"📚 <b>{lesson_title}</b>\n"
        f"Курс: {course_title}\n\n"
        f"💎 +{points_earned} баллов"
    )
    
    return await send_notification(telegram_id, message)


async def send_new_course_notification(
    telegram_id: int,
    course_title: str,
    course_description: str
) -> bool:
    """
    Отправить уведомление о новом курсе
    
    Args:
        telegram_id: Telegram ID пользователя
        course_title: Название курса
        course_description: Описание курса
    
    Returns:
        True если уведомление отправлено успешно
    """
    message = (
        f"🆕 <b>Новый курс доступен!</b>\n\n"
        f"📚 <b>{course_title}</b>\n"
        f"{course_description}\n\n"
        f"Откройте Mini App, чтобы узнать больше!"
    )
    
    return await send_notification(telegram_id, message)


async def send_reminder_notification(
    telegram_id: int,
    course_title: str,
    days_inactive: int
) -> bool:
    """
    Отправить напоминание о продолжении обучения
    
    Args:
        telegram_id: Telegram ID пользователя
        course_title: Название курса
        days_inactive: Количество дней без активности
    
    Returns:
        True если уведомление отправлено успешно
    """
    message = (
        f"⏰ <b>Напоминание</b>\n\n"
        f"Вы не заходили в курс <b>{course_title}</b> уже {days_inactive} дней.\n\n"
        f"Продолжите обучение, чтобы получить сертификат! 🎓"
    )
    
    return await send_notification(telegram_id, message)


async def send_notification_to_user_by_id(
    session: AsyncSession,
    user_id: int,
    message: str,
    parse_mode: Optional[str] = "HTML"
) -> bool:
    """
    Отправить уведомление пользователю по его ID в БД
    
    Args:
        session: SQLAlchemy сессия
        user_id: ID пользователя в БД
        message: Текст сообщения
        parse_mode: Режим парсинга
    
    Returns:
        True если уведомление отправлено успешно
    """
    try:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            logger.warning(f"User with id {user_id} not found")
            return False
        
        return await send_notification(user.telegram_id, message, parse_mode)
    except Exception as e:
        logger.error(f"Error sending notification to user {user_id}: {e}")
        return False


async def broadcast_notification(
    session: AsyncSession,
    message: str,
    user_ids: Optional[list[int]] = None,
    parse_mode: Optional[str] = "HTML"
) -> dict:
    """
    Отправить массовое уведомление пользователям
    
    Args:
        session: SQLAlchemy сессия
        message: Текст сообщения
        user_ids: Список ID пользователей в БД (если None - всем активным)
        parse_mode: Режим парсинга
    
    Returns:
        Словарь с результатами: {"sent": count, "failed": count, "total": count}
    """
    try:
        if user_ids:
            # Отправляем конкретным пользователям
            query = select(User).where(
                User.id.in_(user_ids),
                User.is_active == True
            )
        else:
            # Отправляем всем активным пользователям
            query = select(User).where(User.is_active == True)
        
        result = await session.execute(query)
        users = result.scalars().all()
        
        sent = 0
        failed = 0
        
        for user in users:
            success = await send_notification(user.telegram_id, message, parse_mode)
            if success:
                sent += 1
            else:
                failed += 1
        
        logger.info(f"Broadcast completed: {sent} sent, {failed} failed, {len(users)} total")
        
        return {
            "sent": sent,
            "failed": failed,
            "total": len(users)
        }
    except Exception as e:
        logger.error(f"Error in broadcast: {e}")
        return {"sent": 0, "failed": 0, "total": 0}

