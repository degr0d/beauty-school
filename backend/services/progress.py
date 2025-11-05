"""
Сервис для отслеживания прогресса пользователей
"""

from typing import List, Dict
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from backend.database.models import User, Course, Lesson, UserProgress, UserCourse


async def mark_lesson_completed(
    session: AsyncSession,
    user_id: int,
    lesson_id: int
) -> UserProgress:
    """
    Отмечает урок как пройденный
    
    Args:
        session: Сессия БД
        user_id: ID пользователя
        lesson_id: ID урока
    
    Returns:
        UserProgress: Объект прогресса
    """
    # Проверяем, есть ли уже запись
    result = await session.execute(
        select(UserProgress).where(
            UserProgress.user_id == user_id,
            UserProgress.lesson_id == lesson_id
        )
    )
    progress = result.scalar_one_or_none()
    
    if progress:
        # Обновляем существующую запись
        progress.completed = True
        progress.completed_at = datetime.now()
    else:
        # Создаём новую запись
        progress = UserProgress(
            user_id=user_id,
            lesson_id=lesson_id,
            completed=True,
            completed_at=datetime.now()
        )
        session.add(progress)
    
    await session.commit()
    await session.refresh(progress)
    
    return progress


async def get_course_progress(
    session: AsyncSession,
    user_id: int,
    course_id: int
) -> Dict:
    """
    Получает прогресс пользователя по курсу
    
    Returns:
        dict: {
            "total_lessons": int,
            "completed_lessons": int,
            "progress_percent": float
        }
    """
    # Получаем все уроки курса
    result = await session.execute(
        select(Lesson).where(Lesson.course_id == course_id)
    )
    lessons = result.scalars().all()
    lesson_ids = [l.id for l in lessons]
    
    # Получаем прогресс пользователя
    result = await session.execute(
        select(func.count(UserProgress.id))
        .where(
            UserProgress.user_id == user_id,
            UserProgress.lesson_id.in_(lesson_ids),
            UserProgress.completed == True
        )
    )
    completed_count = result.scalar()
    
    total_lessons = len(lessons)
    progress_percent = (completed_count / total_lessons * 100) if total_lessons > 0 else 0
    
    return {
        "total_lessons": total_lessons,
        "completed_lessons": completed_count,
        "progress_percent": round(progress_percent, 2)
    }


async def check_course_completion(
    session: AsyncSession,
    user_id: int,
    course_id: int
) -> bool:
    """
    Проверяет, завершён ли курс пользователем
    
    Returns:
        bool: True если все уроки пройдены
    """
    progress = await get_course_progress(session, user_id, course_id)
    return progress["progress_percent"] == 100.0


# ========================================
# Пример использования:
# ========================================
# from backend.services.progress import mark_lesson_completed, get_course_progress
# 
# async with async_session() as session:
#     await mark_lesson_completed(session, user_id=1, lesson_id=1)
#     progress = await get_course_progress(session, user_id=1, course_id=1)
#     print(f"Прогресс: {progress['progress_percent']}%")

