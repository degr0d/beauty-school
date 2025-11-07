"""
API эндпоинты для курсов
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_session, Course, Lesson, UserCourse, User, UserProgress
from backend.webapp.schemas import CourseResponse, CourseDetailResponse
from backend.webapp.middleware import get_telegram_user

router = APIRouter()


@router.get("/", response_model=List[CourseResponse])
async def get_courses(
    category: Optional[str] = None,
    is_top: Optional[bool] = None,
    session: AsyncSession = Depends(get_session)
):
    """
    Получить список всех курсов
    
    Query параметры:
    - category: Фильтр по категории (manicure, eyelashes и т.д.)
    - is_top: Показать только топовые курсы
    """
    query = select(Course).where(Course.is_active == True)
    
    # Фильтры
    if category:
        query = query.where(Course.category == category)
    if is_top is not None:
        query = query.where(Course.is_top == is_top)
    
    result = await session.execute(query)
    courses = result.scalars().all()
    
    return courses


@router.get("/{course_id}", response_model=CourseDetailResponse)
async def get_course(
    course_id: int,
    session: AsyncSession = Depends(get_session)
):
    """
    Получить детали курса + список уроков
    """
    # Получаем курс
    result = await session.execute(
        select(Course).where(Course.id == course_id)
    )
    course = result.scalar_one_or_none()
    
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Получаем уроки курса
    result = await session.execute(
        select(Lesson)
        .where(Lesson.course_id == course_id)
        .order_by(Lesson.order)
    )
    lessons = result.scalars().all()
    
    # Формируем ответ
    response = CourseDetailResponse(
        id=course.id,
        title=course.title,
        description=course.description,
        full_description=course.full_description,
        category=course.category,
        cover_image_url=course.cover_image_url,
        is_top=course.is_top,
        price=float(course.price),
        duration_hours=course.duration_hours,
        lessons=[
            {
                "id": lesson.id,
                "title": lesson.title,
                "order": lesson.order,
                "video_duration": lesson.video_duration,
                "is_free": lesson.is_free
            }
            for lesson in lessons
        ]
    )
    
    return response


@router.get("/my/courses", response_model=List[dict])
async def get_my_courses(
    user: dict = Depends(get_telegram_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Получить курсы текущего пользователя с прогрессом
    """
    from sqlalchemy import func
    
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
        select(UserCourse, Course)
        .join(Course, UserCourse.course_id == Course.id)
        .where(UserCourse.user_id == db_user.id)
        .order_by(UserCourse.purchased_at.desc())
    )
    user_courses = result.all()
    
    courses_with_progress = []
    
    for uc, course in user_courses:
        # Подсчитываем прогресс по курсу
        result = await session.execute(
            select(func.count(Lesson.id)).where(Lesson.course_id == course.id)
        )
        total_lessons = result.scalar() or 0
        
        result = await session.execute(
            select(func.count(UserProgress.id))
            .join(Lesson, UserProgress.lesson_id == Lesson.id)
            .where(
                UserProgress.user_id == db_user.id,
                UserProgress.completed == True,
                Lesson.course_id == course.id
            )
        )
        completed_lessons = result.scalar() or 0
        progress_percent = int((completed_lessons / total_lessons * 100)) if total_lessons > 0 else 0
        
        courses_with_progress.append({
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "category": course.category,
            "cover_image_url": course.cover_image_url,
            "is_top": course.is_top,
            "price": float(course.price),
            "duration_hours": course.duration_hours,
            "progress": {
                "total_lessons": total_lessons,
                "completed_lessons": completed_lessons,
                "progress_percent": progress_percent,
                "purchased_at": uc.purchased_at.isoformat() if uc.purchased_at else None,
                "is_completed": uc.is_completed
            }
        })
    
    return courses_with_progress


# ========================================
# Пример запроса:
# ========================================
# GET /api/courses?category=manicure&is_top=true
# GET /api/courses/1
# GET /api/courses/my/courses

