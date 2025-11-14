"""
Сервис для отправки запланированных уведомлений
(напоминания о незавершенных курсах, уведомления о новых курсах)
"""

import asyncio
import logging
from datetime import datetime, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from backend.config import settings
from backend.database import User, Course, UserCourse, UserProgress, Lesson
from backend.services.notifications import send_reminder_notification, send_new_course_notification

logger = logging.getLogger(__name__)


async def send_inactive_course_reminders(session: AsyncSession) -> dict:
    """
    Отправить напоминания пользователям, которые не заходили в курс более 7 дней
    
    Returns:
        Словарь с результатами: {"sent": count, "failed": count, "total": count}
    """
    try:
        # Находим пользователей с незавершенными курсами, которые не были активны более 7 дней
        seven_days_ago = datetime.now() - timedelta(days=7)
        
        # Получаем все незавершенные записи на курсы
        result = await session.execute(
            select(UserCourse, Course, User)
            .join(Course, Course.id == UserCourse.course_id)
            .join(User, User.id == UserCourse.user_id)
            .where(
                UserCourse.is_completed == False,
                User.is_active == True
            )
        )
        user_courses = result.all()
        
        sent = 0
        failed = 0
        
        for uc, course, user in user_courses:
            # Проверяем, когда пользователь последний раз был активен в этом курсе
            last_activity_result = await session.execute(
                select(func.max(UserProgress.completed_at))
                .where(
                    UserProgress.user_id == user.id,
                    UserProgress.completed == True
                )
                .join(Lesson, Lesson.id == UserProgress.lesson_id)
                .where(Lesson.course_id == course.id)
            )
            last_activity = last_activity_result.scalar()
            
            # Если активности не было или было более 7 дней назад
            should_remind = False
            if not last_activity:
                # Если пользователь начал курс, но не завершил ни одного урока
                # Проверяем дату создания записи на курс
                if uc.created_at and uc.created_at < seven_days_ago:
                    should_remind = True
            elif last_activity < seven_days_ago:
                should_remind = True
            
            if should_remind:
                days_inactive = (datetime.now() - (last_activity or uc.created_at or datetime.now())).days
                success = await send_reminder_notification(
                    user.telegram_id,
                    course.title,
                    days_inactive
                )
                if success:
                    sent += 1
                else:
                    failed += 1
        
        logger.info(f"Reminders sent: {sent} sent, {failed} failed, {len(user_courses)} total")
        
        return {
            "sent": sent,
            "failed": failed,
            "total": len(user_courses)
        }
    except Exception as e:
        logger.error(f"Error sending reminders: {e}")
        return {"sent": 0, "failed": 0, "total": 0}


async def send_new_course_notifications(session: AsyncSession, course_id: int) -> dict:
    """
    Отправить уведомления о новом курсе всем активным пользователям
    
    Args:
        session: SQLAlchemy сессия
        course_id: ID нового курса
    
    Returns:
        Словарь с результатами: {"sent": count, "failed": count, "total": count}
    """
    try:
        # Получаем информацию о курсе
        result = await session.execute(
            select(Course).where(Course.id == course_id)
        )
        course = result.scalar_one_or_none()
        
        if not course:
            logger.error(f"Course {course_id} not found")
            return {"sent": 0, "failed": 0, "total": 0}
        
        # Получаем всех активных пользователей
        result = await session.execute(
            select(User).where(User.is_active == True)
        )
        users = result.scalars().all()
        
        sent = 0
        failed = 0
        
        for user in users:
            success = await send_new_course_notification(
                user.telegram_id,
                course.title,
                course.description or ""
            )
            if success:
                sent += 1
            else:
                failed += 1
        
        logger.info(f"New course notifications sent: {sent} sent, {failed} failed, {len(users)} total")
        
        return {
            "sent": sent,
            "failed": failed,
            "total": len(users)
        }
    except Exception as e:
        logger.error(f"Error sending new course notifications: {e}")
        return {"sent": 0, "failed": 0, "total": 0}


async def run_scheduled_notifications():
    """
    Запустить отправку запланированных уведомлений
    Вызывается по расписанию (например, раз в день)
    """
    try:
        # Создаем сессию БД
        engine = create_async_engine(settings.database_url)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with async_session() as session:
            # Отправляем напоминания о незавершенных курсах
            reminders_result = await send_inactive_course_reminders(session)
            logger.info(f"✅ Scheduled reminders completed: {reminders_result}")
        
        await engine.dispose()
    except Exception as e:
        logger.error(f"❌ Error in scheduled notifications: {e}")


if __name__ == "__main__":
    # Для запуска вручную
    asyncio.run(run_scheduled_notifications())


