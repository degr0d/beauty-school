"""
API эндпоинты для прогресса пользователя
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_session, User, Course, Lesson, UserProgress, UserCourse
from backend.webapp.middleware import get_telegram_user
from backend.config import settings

router = APIRouter()


@router.get("/{course_id}")
async def get_course_progress(
    course_id: int,
    user: dict = Depends(get_telegram_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Получить прогресс пользователя по конкретному курсу
    
    Возвращает:
    - Всего уроков
    - Пройдено уроков
    - Процент прогресса
    - Список уроков с отметками
    """
    telegram_id = user["id"]
    
    # АДМИНЫ ВСЕГДА ИМЕЮТ ДОСТУП К ПРОГРЕССУ
    is_admin = telegram_id in settings.admin_ids_list
    
    # Получаем пользователя
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    db_user = result.scalar_one_or_none()
    
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Получаем курс
    result = await session.execute(
        select(Course).where(Course.id == course_id)
    )
    course = result.scalar_one_or_none()
    
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Получаем все уроки курса
    result = await session.execute(
        select(Lesson)
        .where(Lesson.course_id == course_id)
        .order_by(Lesson.order)
    )
    lessons = result.scalars().all()
    
    # Получаем прогресс пользователя
    result = await session.execute(
        select(UserProgress)
        .where(
            UserProgress.user_id == db_user.id,
            UserProgress.lesson_id.in_([lesson.id for lesson in lessons])
        )
    )
    progress_records = result.scalars().all()
    progress_map = {p.lesson_id: p.completed for p in progress_records}
    
    # Формируем ответ
    lessons_data = [
        {
            "id": lesson.id,
            "title": lesson.title,
            "order": lesson.order,
            "completed": progress_map.get(lesson.id, False)
        }
        for lesson in lessons
    ]
    
    total_lessons = len(lessons)
    completed_lessons = sum(1 for l in lessons_data if l["completed"])
    progress_percent = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
    
    return {
        "course_id": course_id,
        "course_title": course.title,
        "total_lessons": total_lessons,
        "completed_lessons": completed_lessons,
        "progress_percent": round(progress_percent, 2),
        "lessons": lessons_data
    }


@router.get("/")
async def get_overall_progress(
    user: dict = Depends(get_telegram_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Получить общий прогресс пользователя по всем курсам
    """
    telegram_id = user["id"]
    
    # Получаем пользователя
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    db_user = result.scalar_one_or_none()
    
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Получаем курсы пользователя
    result = await session.execute(
        select(UserCourse)
        .where(UserCourse.user_id == db_user.id)
    )
    user_courses = result.scalars().all()
    
    total_courses = len(user_courses)
    completed_courses = sum(1 for uc in user_courses if uc.is_completed)
    in_progress_courses = total_courses - completed_courses
    
    # Подсчитываем общее количество пройденных уроков
    result = await session.execute(
        select(func.count(UserProgress.id))
        .where(
            UserProgress.user_id == db_user.id,
            UserProgress.completed == True
        )
    )
    total_lessons_completed = result.scalar() or 0
    
    return {
        "total_courses": total_courses,
        "completed_courses": completed_courses,
        "in_progress_courses": in_progress_courses,
        "total_lessons_completed": total_lessons_completed
    }


# ========================================
# Пример запроса:
# ========================================
# GET /api/progress/1  (прогресс по курсу ID=1)
# GET /api/progress    (общий прогресс)

