"""
Управление пользователями (для админов)
"""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select

from backend.database import async_session, User, Course, UserCourse
from datetime import datetime
from backend.config import settings
from backend.admin_bot.filters import AdminFilter

router = Router()

# Фильтр для админов - применяется ко всем обработчикам в этом роутере
router.message.filter(AdminFilter())


def is_admin(user_id: int) -> bool:
    """Проверка, является ли пользователь админом"""
    return user_id in settings.admin_ids_list


@router.message(Command("users"))
async def list_users(message: Message):
    """
    Список последних пользователей
    """
    
    async with async_session() as session:
        # Получаем последних 10 пользователей
        result = await session.execute(
            select(User).order_by(User.created_at.desc()).limit(10)
        )
        users = result.scalars().all()
    
    if not users:
        await message.answer("📭 Пользователей пока нет")
        return
    
    users_list = []
    for u in users:
        user_text = (
            f"• <b>{u.full_name}</b>\n"
            f"  Telegram: <code>{u.telegram_id}</code>\n"
            f"  Телефон: {u.phone}\n"
            f"  {u.created_at.strftime('%d.%m.%Y')}"
        )
        users_list.append(user_text)
    
    users_text = "\n\n".join(users_list)
    
    await message.answer(
        f"👥 <b>Последние 10 пользователей:</b>\n\n{users_text}\n\n"
        f"💡 Используйте /user <telegram_id> для детальной информации",
        parse_mode="HTML"
    )


@router.message(Command("user"))
async def get_user_info(message: Message):
    """
    Детальная информация о пользователе
    
    Формат: /user <telegram_id>
    """
    
    # Извлекаем telegram_id из команды
    args = message.text.split()[1:] if message.text else []
    if not args:
        await message.answer(
            "❌ Укажите Telegram ID пользователя\n\n"
            "Формат: <code>/user 123456789</code>",
            parse_mode="HTML"
        )
        return
    
    try:
        telegram_id = int(args[0])
    except ValueError:
        await message.answer("❌ Неверный формат Telegram ID")
        return
    
    from sqlalchemy import select, func
    from backend.database.models import UserCourse, UserProgress, Lesson, Course
    
    async with async_session() as session:
        # Получаем пользователя
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            await message.answer(f"❌ Пользователь с ID {telegram_id} не найден")
            return
        
        # Получаем курсы пользователя
        result = await session.execute(
            select(UserCourse, Course)
            .join(Course, UserCourse.course_id == Course.id)
            .where(UserCourse.user_id == user.id)
        )
        user_courses = result.all()
        
        # Подсчитываем прогресс
        total_lessons = 0
        completed_lessons = 0
        
        # Формируем информацию о курсах
        courses_list = []
        
        for uc, course in user_courses:
            # Подсчитываем прогресс по курсу
            result = await session.execute(
                select(func.count(Lesson.id)).where(Lesson.course_id == course.id)
            )
            course_total = result.scalar() or 0
            total_lessons += course_total
            
            result = await session.execute(
                select(func.count(UserProgress.id))
                .join(Lesson, UserProgress.lesson_id == Lesson.id)
                .where(
                    UserProgress.user_id == user.id,
                    UserProgress.completed == True,
                    Lesson.course_id == course.id
                )
            )
            course_completed = result.scalar() or 0
            completed_lessons += course_completed
            
            progress = int((course_completed / course_total * 100)) if course_total > 0 else 0
            
            courses_list.append(
                f"  • {course.title}\n"
                f"    Прогресс: {course_completed}/{course_total} ({progress}%)"
            )
        
        courses_text = "\n".join(courses_list) if courses_list else "  Курсов пока нет"
    
    user_info = (
        f"👤 <b>Информация о пользователе</b>\n\n"
        f"📝 ФИО: {user.full_name}\n"
        f"🆔 Telegram ID: <code>{user.telegram_id}</code>\n"
        f"{f'👤 Username: @{user.username}' if user.username else ''}\n"
        f"📞 Телефон: {user.phone}\n"
        f"{f'📍 Город: {user.city}' if user.city else ''}\n"
        f"⭐ Баллов: {user.points}\n"
        f"📅 Регистрация: {user.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
        f"📚 <b>Курсы ({len(user_courses)}):</b>\n{courses_text}\n\n"
        f"📊 <b>Общий прогресс:</b>\n"
        f"  Пройдено уроков: {completed_lessons}/{total_lessons}\n"
        f"  Процент: {int((completed_lessons / total_lessons * 100)) if total_lessons > 0 else 0}%"
    )
    
    await message.answer(user_info, parse_mode="HTML")


@router.message(Command("grant_access"))
async def grant_access(message: Message):
    """
    ВРЕМЕННАЯ КОМАНДА: Выдать доступ пользователю (как будто оплатил)
    
    Формат: /grant_access <telegram_id> [course_id]
    
    Если course_id не указан - даёт доступ ко всем курсам
    Если указан - даёт доступ только к указанному курсу
    """
    
    # Извлекаем аргументы
    args = message.text.split()[1:] if message.text else []
    if not args:
        await message.answer(
            "❌ Укажите Telegram ID пользователя\n\n"
            "Формат: <code>/grant_access 123456789</code>\n"
            "Или: <code>/grant_access 123456789 1</code> (для конкретного курса)\n\n"
            "⚠️ <b>ВРЕМЕННАЯ КОМАНДА</b> - для тестирования",
            parse_mode="HTML"
        )
        return
    
    try:
        telegram_id = int(args[0])
        course_id = int(args[1]) if len(args) > 1 else None
    except ValueError:
        await message.answer("❌ Неверный формат. Используйте числа для ID")
        return
    
    async with async_session() as session:
        # Получаем пользователя
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            await message.answer(f"❌ Пользователь с ID {telegram_id} не найден")
            return
        
        # Получаем курсы для выдачи доступа
        if course_id:
            # Конкретный курс
            result = await session.execute(
                select(Course).where(Course.id == course_id)
            )
            courses = [result.scalar_one_or_none()]
            if not courses[0]:
                await message.answer(f"❌ Курс с ID {course_id} не найден")
                return
        else:
            # Все курсы
            result = await session.execute(select(Course))
            courses = result.scalars().all()
            if not courses:
                await message.answer("❌ В базе нет курсов")
                return
        
        # Проверяем и создаём записи UserCourse
        granted_count = 0
        already_had_count = 0
        
        for course in courses:
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
        if course_id:
            course_name = courses[0].title if courses else "неизвестный курс"
            if granted_count > 0:
                response = (
                    f"✅ <b>Доступ выдан!</b>\n\n"
                    f"👤 Пользователь: {user.full_name} (<code>{telegram_id}</code>)\n"
                    f"📚 Курс: {course_name}\n\n"
                    f"💡 Теперь пользователь может получить доступ к платформе"
                )
            else:
                response = (
                    f"ℹ️ <b>Доступ уже был</b>\n\n"
                    f"👤 Пользователь: {user.full_name} (<code>{telegram_id}</code>)\n"
                    f"📚 Курс: {course_name}\n\n"
                    f"У пользователя уже есть доступ к этому курсу"
                )
        else:
            response = (
                f"✅ <b>Доступ выдан!</b>\n\n"
                f"👤 Пользователь: {user.full_name} (<code>{telegram_id}</code>)\n"
                f"📚 Курсов добавлено: {granted_count}\n"
                f"{f'ℹ️ Уже имел доступ к: {already_had_count}' if already_had_count > 0 else ''}\n\n"
                f"💡 Теперь пользователь может получить доступ к платформе"
            )
        
        await message.answer(response, parse_mode="HTML")


@router.message(Command("revoke_access"))
async def revoke_access(message: Message):
    """
    ВРЕМЕННАЯ КОМАНДА: Отозвать доступ пользователя
    
    Формат: /revoke_access <telegram_id> [course_id]
    
    Если course_id не указан - отзывает доступ ко всем курсам
    Если указан - отзывает доступ только к указанному курсу
    """
    
    # Извлекаем аргументы
    args = message.text.split()[1:] if message.text else []
    if not args:
        await message.answer(
            "❌ Укажите Telegram ID пользователя\n\n"
            "Формат: <code>/revoke_access 123456789</code>\n"
            "Или: <code>/revoke_access 123456789 1</code> (для конкретного курса)\n\n"
            "⚠️ <b>ВРЕМЕННАЯ КОМАНДА</b> - для тестирования",
            parse_mode="HTML"
        )
        return
    
    try:
        telegram_id = int(args[0])
        course_id = int(args[1]) if len(args) > 1 else None
    except ValueError:
        await message.answer("❌ Неверный формат. Используйте числа для ID")
        return
    
    async with async_session() as session:
        # Получаем пользователя
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            await message.answer(f"❌ Пользователь с ID {telegram_id} не найден")
            return
        
        # Удаляем записи UserCourse
        if course_id:
            result = await session.execute(
                select(UserCourse).where(
                    UserCourse.user_id == user.id,
                    UserCourse.course_id == course_id
                )
            )
            user_courses = result.scalars().all()
        else:
            result = await session.execute(
                select(UserCourse).where(UserCourse.user_id == user.id)
            )
            user_courses = result.scalars().all()
        
        if not user_courses:
            await message.answer(
                f"ℹ️ У пользователя {user.full_name} (<code>{telegram_id}</code>) нет доступа к курсам",
                parse_mode="HTML"
            )
            return
        
        revoked_count = len(user_courses)
        
        # Получаем названия курсов для сообщения
        if course_id:
            result = await session.execute(
                select(Course).where(Course.id == course_id)
            )
            course = result.scalar_one_or_none()
            course_name = course.title if course else f"курс #{course_id}"
        else:
            course_name = "всем курсам"
        
        # Удаляем записи
        for uc in user_courses:
            await session.delete(uc)
        
        await session.commit()
        
        response = (
            f"✅ <b>Доступ отозван!</b>\n\n"
            f"👤 Пользователь: {user.full_name} (<code>{telegram_id}</code>)\n"
            f"📚 Отозван доступ к: {course_name}\n"
            f"🗑️ Удалено записей: {revoked_count}\n\n"
            f"⚠️ Пользователь больше не сможет получить доступ к платформе"
        )
        
        await message.answer(response, parse_mode="HTML")


# ========================================
# Пример команды:
# ========================================
# /users - Список последних пользователей
# /user <telegram_id> - Информация о пользователе
# /grant_access <telegram_id> - Выдать доступ ко всем курсам
# /grant_access <telegram_id> <course_id> - Выдать доступ к конкретному курсу
# /revoke_access <telegram_id> - Отозвать доступ ко всем курсам
# /revoke_access <telegram_id> <course_id> - Отозвать доступ к конкретному курсу

