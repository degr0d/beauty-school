"""
Сервис для работы с курсами
"""

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models import Course, Lesson, UserCourse


async def get_all_courses(
    session: AsyncSession,
    category: Optional[str] = None,
    is_top: Optional[bool] = None
) -> List[Course]:
    """
    Получает список всех активных курсов
    
    Args:
        session: Сессия БД
        category: Фильтр по категории
        is_top: Показать только топовые курсы
    
    Returns:
        List[Course]: Список курсов
    """
    query = select(Course).where(Course.is_active == True)
    
    if category:
        query = query.where(Course.category == category)
    if is_top is not None:
        query = query.where(Course.is_top == is_top)
    
    result = await session.execute(query)
    return result.scalars().all()


async def get_course_by_id(session: AsyncSession, course_id: int) -> Optional[Course]:
    """
    Получает курс по ID
    """
    result = await session.execute(
        select(Course).where(Course.id == course_id)
    )
    return result.scalar_one_or_none()


async def get_course_lessons(session: AsyncSession, course_id: int) -> List[Lesson]:
    """
    Получает список уроков курса
    """
    result = await session.execute(
        select(Lesson)
        .where(Lesson.course_id == course_id)
        .order_by(Lesson.order)
    )
    return result.scalars().all()


async def grant_course_access(session: AsyncSession, user_id: int, course_id: int):
    """
    Даёт пользователю доступ к курсу
    
    Args:
        session: Сессия БД
        user_id: ID пользователя
        course_id: ID курса
    """
    # Проверяем, есть ли уже доступ
    result = await session.execute(
        select(UserCourse).where(
            UserCourse.user_id == user_id,
            UserCourse.course_id == course_id
        )
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        # Доступ уже есть
        return existing
    
    # Создаём новую запись
    user_course = UserCourse(
        user_id=user_id,
        course_id=course_id
    )
    
    session.add(user_course)
    await session.commit()
    await session.refresh(user_course)
    
    return user_course


# ========================================
# Пример использования:
# ========================================
# from backend.services.courses import get_all_courses, grant_course_access
# 
# async with async_session() as session:
#     courses = await get_all_courses(session, category="manicure")
#     await grant_course_access(session, user_id=1, course_id=1)

