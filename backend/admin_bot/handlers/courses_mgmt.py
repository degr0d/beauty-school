"""
Управление курсами (для админов)
"""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select

from backend.database import async_session, Course
from backend.config import settings
from backend.admin_bot.filters import AdminFilter
from backend.database.seed_data import seed_courses, seed_achievements, seed_communities

router = Router()

# Фильтр для админов - применяется ко всем обработчикам в этом роутере
router.message.filter(AdminFilter())


def is_admin(user_id: int) -> bool:
    """Проверка, является ли пользователь админом"""
    return user_id in settings.admin_ids_list


@router.message(Command("courses"))
async def list_courses(message: Message):
    """
    Список всех курсов
    """
    
    from sqlalchemy import func, select
    from backend.database.models import Lesson, UserCourse
    
    async with async_session() as session:
        result = await session.execute(
            select(Course).order_by(Course.created_at.desc())
        )
        courses = result.scalars().all()
    
    if not courses:
        await message.answer("📭 Курсов пока нет")
        return
    
    courses_list = []
    for c in courses:
        # Подсчитываем количество уроков и записей
        result = await session.execute(
            select(func.count(Lesson.id)).where(Lesson.course_id == c.id)
        )
        lessons_count = result.scalar() or 0
        
        result = await session.execute(
            select(func.count(UserCourse.id)).where(UserCourse.course_id == c.id)
        )
        enrollments = result.scalar() or 0
        
        course_text = (
            f"• <b>{c.title}</b>\n"
            f"  ID: {c.id} | Категория: {c.category}\n"
            f"  Уроков: {lessons_count} | Записей: {enrollments}\n"
            f"  {'🔥 Топ' if c.is_top else ''} "
            f"{'✅ Активен' if c.is_active else '❌ Неактивен'}"
        )
        courses_list.append(course_text)
    
    courses_text = "\n\n".join(courses_list)
    
    await message.answer(
        f"📚 <b>Все курсы ({len(courses)}):</b>\n\n{courses_text}",
        parse_mode="HTML"
    )


@router.message(Command("course"))
async def get_course_info(message: Message):
    """
    Детальная информация о курсе
    
    Формат: /course <course_id>
    """
    args = message.text.split()[1:] if message.text else []
    if not args:
        await message.answer(
            "❌ Укажите ID курса\n\n"
            "Формат: <code>/course 1</code>",
            parse_mode="HTML"
        )
        return
    
    try:
        course_id = int(args[0])
    except ValueError:
        await message.answer("❌ Неверный формат ID курса")
        return
    
    from sqlalchemy import select, func
    from backend.database.models import Lesson, UserCourse, UserProgress
    
    async with async_session() as session:
        result = await session.execute(
            select(Course).where(Course.id == course_id)
        )
        course = result.scalar_one_or_none()
        
        if not course:
            await message.answer(f"❌ Курс с ID {course_id} не найден")
            return
        
        # Получаем уроки
        result = await session.execute(
            select(Lesson).where(Lesson.course_id == course_id).order_by(Lesson.order)
        )
        lessons = result.scalars().all()
        
        # Подсчитываем статистику
        result = await session.execute(
            select(func.count(UserCourse.id)).where(UserCourse.course_id == course_id)
        )
        enrollments = result.scalar() or 0
        
        result = await session.execute(
            select(func.count(UserProgress.id))
            .join(Lesson, UserProgress.lesson_id == Lesson.id)
            .where(Lesson.course_id == course_id, UserProgress.completed == True)
        )
        completed_lessons = result.scalar() or 0
    
    lessons_text = "\n".join([
        f"  {i+1}. {lesson.title} {'✅' if lesson.is_free else '🔒'}"
        for i, lesson in enumerate(lessons)
    ]) if lessons else "  Уроков нет"
    
    course_info = (
        f"📚 <b>{course.title}</b>\n\n"
        f"📝 Описание: {course.description}\n"
        f"🏷️ Категория: {course.category}\n"
        f"💰 Цена: {course.price} ₽\n"
        f"⏱ Длительность: {course.duration_hours or 'Не указано'} ч\n"
        f"{'🔥 Топ курс' if course.is_top else ''}\n"
        f"{'✅ Активен' if course.is_active else '❌ Неактивен'}\n\n"
        f"📊 <b>Статистика:</b>\n"
        f"  Уроков: {len(lessons)}\n"
        f"  Записей: {enrollments}\n"
        f"  Пройдено уроков: {completed_lessons}\n\n"
        f"📖 <b>Уроки:</b>\n{lessons_text}"
    )
    
    await message.answer(course_info, parse_mode="HTML")


@router.message(Command("seed_data"))
async def create_test_data(message: Message):
    """
    Создать тестовые данные (курсы, достижения, сообщества)
    Для тестирования функционала
    """
    await message.answer("🌱 Создаю тестовые данные...\n\nЭто может занять несколько секунд...")
    
    try:
        # Создаем курсы
        await seed_courses()
        courses_msg = "✅ Курсы созданы"
    except Exception as e:
        courses_msg = f"❌ Ошибка создания курсов: {str(e)}"
    
    try:
        # Создаем достижения
        await seed_achievements()
        achievements_msg = "✅ Достижения созданы"
    except Exception as e:
        achievements_msg = f"❌ Ошибка создания достижений: {str(e)}"
    
    try:
        # Создаем сообщества
        await seed_communities()
        communities_msg = "✅ Сообщества созданы"
    except Exception as e:
        communities_msg = f"❌ Ошибка создания сообществ: {str(e)}"
    
    result = (
        f"📊 <b>Результат создания тестовых данных:</b>\n\n"
        f"{courses_msg}\n"
        f"{achievements_msg}\n"
        f"{communities_msg}\n\n"
        f"💡 Теперь можно тестировать функционал!"
    )
    
    await message.answer(result, parse_mode="HTML")


# ========================================
# TODO: Добавить команды для создания/редактирования курсов
# ========================================
# /create_course - Создать новый курс (FSM)
# /edit_course {id} - Редактировать курс
# /delete_course {id} - Удалить курс
# /toggle_course {id} - Включить/выключить курс


# ========================================
# Пример команды:
# ========================================
# /courses - Список всех курсов
# /seed_data - Создать тестовые данные

