"""
Аналитика для админов
"""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select, func
from datetime import datetime, timedelta

from backend.database import async_session, User, Course, UserCourse, UserProgress
from backend.config import settings
from backend.admin_bot.filters import AdminFilter

router = Router()

# Фильтр для админов - применяется ко всем обработчикам в этом роутере
router.message.filter(AdminFilter())


def is_admin(user_id: int) -> bool:
    """
    Проверка, является ли пользователь админом
    """
    return user_id in settings.admin_ids_list


@router.message(Command("start"))
async def admin_start(message: Message):
    """
    Приветствие админа
    Обрабатывает /start только для админов (фильтр AdminFilter)
    """
    print(f"✅ [AdminBot] Получена команда /start от user_id={message.from_user.id}")
    
    welcome_text = (
        "👨‍💼 <b>Админ-панель бьюти-школы</b>\n\n"
        "Доступные команды:\n"
        "/stats - Общая статистика\n"
        "/users - Список пользователей\n"
        "/user ID - Информация о пользователе\n"
        "/courses - Управление курсами\n"
        "/course ID - Детали курса\n"
        "/analytics - Детальная аналитика\n"
        "/seed_data - Создать тестовые данные\n\n"
        "🔧 <b>Временные команды (для тестирования):</b>\n"
        "/grant_access TELEGRAM_ID - Выдать доступ ко всем курсам\n"
        "/grant_access TELEGRAM_ID COURSE_ID - Выдать доступ к курсу\n"
        "/revoke_access TELEGRAM_ID - Отозвать доступ\n"
    )
    
    await message.answer(welcome_text, parse_mode="HTML")


@router.message(Command("stats"))
async def get_stats(message: Message):
    """
    Общая статистика
    """
    
    async with async_session() as session:
        # Всего пользователей
        result = await session.execute(select(func.count(User.id)))
        total_users = result.scalar()
        
        # Новых за сегодня
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        result = await session.execute(
            select(func.count(User.id)).where(User.created_at >= today)
        )
        new_today = result.scalar()
        
        # Новых за неделю
        week_ago = datetime.now() - timedelta(days=7)
        result = await session.execute(
            select(func.count(User.id)).where(User.created_at >= week_ago)
        )
        new_week = result.scalar()
        
        # Всего курсов
        result = await session.execute(select(func.count(Course.id)))
        total_courses = result.scalar()
        
        # Активных курсов
        result = await session.execute(
            select(func.count(Course.id)).where(Course.is_active == True)
        )
        active_courses = result.scalar()
        
        # Всего записей на курсы
        result = await session.execute(select(func.count(UserCourse.id)))
        total_enrollments = result.scalar()
    
    stats_text = (
        "📊 <b>Общая статистика</b>\n\n"
        f"👥 Всего пользователей: {total_users}\n"
        f"   ├─ Новых за сегодня: {new_today}\n"
        f"   └─ Новых за неделю: {new_week}\n\n"
        f"📚 Курсов: {active_courses} / {total_courses} (активных)\n"
        f"📝 Записей на курсы: {total_enrollments}\n"
    )
    
    await message.answer(stats_text, parse_mode="HTML")


@router.message(Command("analytics"))
async def get_analytics(message: Message):
    """
    Детальная аналитика
    """
    
    async with async_session() as session:
        # Топ-5 популярных курсов
        from sqlalchemy import desc
        result = await session.execute(
            select(Course.title, func.count(UserCourse.id).label("enrollments"))
            .join(UserCourse, UserCourse.course_id == Course.id, isouter=True)
            .group_by(Course.id, Course.title)
            .order_by(desc("enrollments"))
            .limit(5)
        )
        top_courses = result.all()
        
        # Всего пройденных уроков
        result = await session.execute(
            select(func.count(UserProgress.id)).where(UserProgress.completed == True)
        )
        total_completed = result.scalar()
    
    # Формируем текст
    courses_text = "\n".join([f"   {i+1}. {c.title} - {c.enrollments} записей" for i, c in enumerate(top_courses)])
    
    analytics_text = (
        "📈 <b>Детальная аналитика</b>\n\n"
        f"🔥 Топ-5 популярных курсов:\n{courses_text}\n\n"
        f"✅ Всего пройдено уроков: {total_completed}\n"
    )
    
    await message.answer(analytics_text, parse_mode="HTML")


# ========================================
# Пример команд:
# ========================================
# /start - Приветствие
# /stats - Общая статистика
# /analytics - Детальная аналитика

