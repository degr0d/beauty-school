"""
Обработчики дополнительных команд бота
/courses, /profile, /help
"""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select
from datetime import datetime

from backend.database import async_session, User, Course, UserCourse

router = Router()


@router.message(Command("help"))
async def cmd_help(message: Message):
    """
    Команда /help - справка по командам
    """
    help_text = (
        "<b>📚 Доступные команды:</b>\n\n"
        "/start - Главное меню\n"
        "/courses - Список всех курсов\n"
        "/profile - Твой профиль\n"
        "/help - Эта справка\n\n"
        "<i>Если есть вопросы - пиши в поддержку!</i>"
    )
    
    await message.answer(help_text, parse_mode="HTML")


@router.message(Command("profile"))
async def cmd_profile(message: Message):
    """
    Команда /profile - показать профиль пользователя
    """
    telegram_id = message.from_user.id
    
    # Получаем пользователя из БД
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
    
    if not user:
        await message.answer(
            "❌ Ты ещё не зарегистрирован!\n\n"
            "Нажми /start чтобы начать 🚀"
        )
        return
    
    # Проверяем формат created_at для диагностики
    created_at_str = "❓ Неизвестно"
    created_at_type = "unknown"
    try:
        if hasattr(user.created_at, 'isoformat'):
            created_at_str = user.created_at.isoformat()[:19]  # Берем только дату и время
            created_at_type = "datetime (OK)"
        elif hasattr(user.created_at, 'strftime'):
            created_at_str = user.created_at.strftime('%d.%m.%Y %H:%M:%S')
            created_at_type = "datetime (OK)"
        else:
            created_at_str = str(user.created_at)
            created_at_type = f"{type(user.created_at).__name__} (⚠️)"
    except Exception as e:
        created_at_str = f"Ошибка: {str(e)}"
        created_at_type = "ERROR"
    
    # Формируем информацию о профиле с диагностикой
    profile_text = (
        f"<b>👤 Твой профиль</b>\n\n"
        f"📝 ФИО: {user.full_name}\n"
        f"📞 Телефон: {user.phone}\n"
        f"🔗 Username: @{user.username or 'не указан'}\n"
        f"🏆 Баллы: {user.points}\n"
        f"📅 Дата регистрации: {created_at_str}\n"
    )
    
    if user.city:
        profile_text += f"📍 Город: {user.city}\n"
    
    # Диагностическая информация (только для отладки)
    profile_text += (
        f"\n🔍 <b>Диагностика:</b>\n"
        f"ID: {user.id}\n"
        f"Telegram ID: {user.telegram_id}\n"
        f"Created at тип: {created_at_type}\n"
    )
    
    profile_text += f"\n💡 Открой Mini App для редактирования профиля!"
    
    await message.answer(profile_text, parse_mode="HTML")


@router.message(Command("courses"))
async def cmd_courses(message: Message):
    """
    Команда /courses - список всех курсов
    """
    telegram_id = message.from_user.id
    
    # Проверяем, зарегистрирован ли пользователь
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            await message.answer(
                "❌ Ты ещё не зарегистрирован!\n\n"
                "Нажми /start чтобы начать 🚀"
            )
            return
        
        # Получаем все курсы
        result = await session.execute(select(Course).order_by(Course.category, Course.title))
        courses = result.scalars().all()
    
    if not courses:
        await message.answer(
            "📚 <b>Курсы пока не добавлены</b>\n\n"
            "Скоро здесь появятся крутые курсы!",
            parse_mode="HTML"
        )
        return
    
    # Группируем курсы по категориям
    courses_by_category = {}
    for course in courses:
        if course.category not in courses_by_category:
            courses_by_category[course.category] = []
        courses_by_category[course.category].append(course)
    
    # Формируем текст сообщения
    message_text = "<b>📚 Доступные курсы:</b>\n\n"
    
    # Эмодзи для категорий
    category_emojis = {
        "Маникюр и педикюр": "💅",
        "Ресницы и брови": "👁",
        "Подология": "🦶",
        "Своё дело": "💼",
    }
    
    for category, category_courses in courses_by_category.items():
        emoji = category_emojis.get(category, "📖")
        message_text += f"\n{emoji} <b>{category}</b>\n"
        
        for course in category_courses:
            top_badge = " ⭐" if course.is_top else ""
            price_text = f"{course.price} ₽" if course.price > 0 else "Бесплатно"
            
            message_text += (
                f"  • <b>{course.title}</b>{top_badge}\n"
                f"    {course.description}\n"
                f"    Цена: {price_text}\n"
            )
            
            if course.duration_hours:
                message_text += f"    Длительность: {course.duration_hours} ч.\n"
            
            message_text += "\n"
    
    message_text += (
        "\n<i>Чтобы записаться на курс, открой приложение через /start</i>"
    )
    
    await message.answer(message_text, parse_mode="HTML")


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """
    Команда /stats - статистика обучения (бонусная)
    """
    telegram_id = message.from_user.id
    
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            await message.answer(
                "❌ Ты ещё не зарегистрирован!\n\n"
                "Нажми /start чтобы начать 🚀"
            )
            return
    
    from sqlalchemy import func
    from backend.database.models import UserCourse, UserProgress, UserAchievement
    
    # Подсчитываем статистику
    result = await session.execute(
        select(func.count(UserCourse.id)).where(UserCourse.user_id == user.id)
    )
    total_courses = result.scalar() or 0
    
    result = await session.execute(
        select(func.count(UserCourse.id))
        .where(UserCourse.user_id == user.id, UserCourse.is_completed == True)
    )
    completed_courses = result.scalar() or 0
    
    result = await session.execute(
        select(func.count(UserProgress.id))
        .where(UserProgress.user_id == user.id, UserProgress.completed == True)
    )
    completed_lessons = result.scalar() or 0
    
    result = await session.execute(
        select(func.count(UserAchievement.id)).where(UserAchievement.user_id == user.id)
    )
    achievements_count = result.scalar() or 0
    
    stats_text = (
        f"<b>📊 Твоя статистика</b>\n\n"
        f"🏆 Баллов заработано: {user.points}\n"
        f"📚 Курсов записано: {total_courses}\n"
        f"   ├─ Завершено: {completed_courses}\n"
        f"   └─ В процессе: {total_courses - completed_courses}\n"
        f"✅ Уроков завершено: {completed_lessons}\n"
        f"🏅 Достижений получено: {achievements_count}\n\n"
        f"<i>Продолжай обучение чтобы улучшить показатели!</i>"
    )
    
    await message.answer(stats_text, parse_mode="HTML")


# ========================================
# ⚠️ ВРЕМЕННАЯ КОМАНДА - УДАЛИТЬ ПОСЛЕ ТЕСТИРОВАНИЯ!
# ========================================
@router.message(Command("free8"))
async def cmd_free8(message: Message):
    """
    ⚠️ ВРЕМЕННАЯ СЕКРЕТНАЯ КОМАНДА - УДАЛИТЬ ПОСЛЕ ТЕСТИРОВАНИЯ!
    
    Выдает доступ ко всем курсам пользователю, который вызвал команду.
    Система будет считать, что пользователь купил все курсы.
    """
    telegram_id = message.from_user.id
    
    async with async_session() as session:
        # Получаем пользователя
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            await message.answer(
                "❌ Ты ещё не зарегистрирован!\n\n"
                "Нажми /start чтобы начать 🚀"
            )
            return
        
        # Получаем все курсы (включая неактивные)
        result = await session.execute(select(Course))
        all_courses = result.scalars().all()
        
        # Если курсов нет - создаем тестовый курс для тестирования
        if not all_courses:
            test_course = Course(
                title="Тестовый курс",
                description="Временный курс для тестирования функционала",
                full_description="Этот курс создан автоматически командой /free8 для тестирования. Вы можете удалить его позже.",
                category="Тестирование",
                is_top=False,
                price=0,
                duration_hours=1,
                is_active=True
            )
            session.add(test_course)
            await session.commit()
            await session.refresh(test_course)
            
            all_courses = [test_course]
            
            await message.answer(
                f"⚠️ <b>В базе не было курсов</b>\n\n"
                f"✅ Создан тестовый курс для тестирования\n"
                f"📚 Теперь выдаю доступ к курсу...\n\n"
                f"💡 <i>Этот курс можно удалить позже через админ-панель</i>",
                parse_mode="HTML"
            )
        
        # Выдаем доступ ко всем курсам
        granted_count = 0
        already_had_count = 0
        
        for course in all_courses:
            # Проверяем, есть ли уже доступ
            result = await session.execute(
                select(UserCourse).where(
                    UserCourse.user_id == user.id,
                    UserCourse.course_id == course.id
                )
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                already_had_count += 1
                continue
            
            # Создаём новую запись
            user_course = UserCourse(
                user_id=user.id,
                course_id=course.id,
                purchased_at=datetime.now()
            )
            session.add(user_course)
            granted_count += 1
        
        await session.commit()
        
        # Формируем ответ
        if granted_count > 0:
            response = (
                f"✅ <b>Доступ ко всем курсам выдан!</b>\n\n"
                f"📚 Выдано курсов: {granted_count}\n"
                f"📚 Уже было: {already_had_count}\n"
                f"📚 Всего курсов: {len(all_courses)}\n\n"
                f"💡 Теперь у тебя есть доступ ко всем материалам платформы!"
            )
        else:
            response = (
                f"ℹ️ У тебя уже есть доступ ко всем курсам!\n\n"
                f"📚 Всего курсов: {len(all_courses)}\n"
                f"📚 У тебя доступ: {already_had_count}"
            )
        
        await message.answer(response, parse_mode="HTML")

