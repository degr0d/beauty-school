"""
API эндпоинты для аналитики (только для админов)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from typing import List
from pydantic import BaseModel

from backend.database import get_session, User, Course, UserCourse, UserProgress, Payment, Certificate, Lesson
from backend.webapp.middleware import get_telegram_user
from backend.config import settings

router = APIRouter()


def check_admin(user: dict) -> bool:
    """Проверка, является ли пользователь админом"""
    telegram_id = user.get("id")
    if not telegram_id:
        return False
    return int(telegram_id) in settings.admin_ids_list


# ========================================
# Схемы ответов
# ========================================
class UserStatsResponse(BaseModel):
    total_users: int
    new_today: int
    new_week: int
    active_users: int

class CourseStatsResponse(BaseModel):
    total_courses: int
    active_courses: int
    total_enrollments: int
    completed_courses: int

class RevenueStatsResponse(BaseModel):
    total_revenue: float
    revenue_today: float
    revenue_week: float
    revenue_month: float
    total_payments: int
    successful_payments: int

class ConversionFunnelResponse(BaseModel):
    visitors: int
    registered: int
    purchased: int
    started_learning: int
    completed_course: int

class CourseAnalyticsResponse(BaseModel):
    course_id: int
    course_title: str
    enrollments: int
    completions: int
    completion_rate: float
    average_progress: float
    revenue: float

class DailyStatsResponse(BaseModel):
    date: str
    new_users: int
    new_enrollments: int
    completed_lessons: int
    revenue: float


# ========================================
# Эндпоинты
# ========================================
@router.get("/stats/users", response_model=UserStatsResponse)
async def get_user_stats(
    user: dict = Depends(get_telegram_user),
    session: AsyncSession = Depends(get_session)
):
    """Статистика по пользователям (только для админов)"""
    if not check_admin(user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Всего пользователей
    result = await session.execute(select(func.count(User.id)))
    total_users = result.scalar() or 0
    
    # Новых за сегодня
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    result = await session.execute(
        select(func.count(User.id)).where(User.created_at >= today)
    )
    new_today = result.scalar() or 0
    
    # Новых за неделю
    week_ago = datetime.now() - timedelta(days=7)
    result = await session.execute(
        select(func.count(User.id)).where(User.created_at >= week_ago)
    )
    new_week = result.scalar() or 0
    
    # Активных пользователей (за последние 30 дней)
    month_ago = datetime.now() - timedelta(days=30)
    result = await session.execute(
        select(func.count(func.distinct(UserProgress.user_id)))
        .where(UserProgress.completed_at >= month_ago)
    )
    active_users = result.scalar() or 0
    
    return UserStatsResponse(
        total_users=total_users,
        new_today=new_today,
        new_week=new_week,
        active_users=active_users
    )


@router.get("/stats/courses", response_model=CourseStatsResponse)
async def get_course_stats(
    user: dict = Depends(get_telegram_user),
    session: AsyncSession = Depends(get_session)
):
    """Статистика по курсам (только для админов)"""
    if not check_admin(user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Всего курсов
    result = await session.execute(select(func.count(Course.id)))
    total_courses = result.scalar() or 0
    
    # Активных курсов
    result = await session.execute(
        select(func.count(Course.id)).where(Course.is_active == True)
    )
    active_courses = result.scalar() or 0
    
    # Всего записей на курсы
    result = await session.execute(select(func.count(UserCourse.id)))
    total_enrollments = result.scalar() or 0
    
    # Завершенных курсов
    result = await session.execute(
        select(func.count(UserCourse.id)).where(UserCourse.is_completed == True)
    )
    completed_courses = result.scalar() or 0
    
    return CourseStatsResponse(
        total_courses=total_courses,
        active_courses=active_courses,
        total_enrollments=total_enrollments,
        completed_courses=completed_courses
    )


@router.get("/stats/revenue", response_model=RevenueStatsResponse)
async def get_revenue_stats(
    user: dict = Depends(get_telegram_user),
    session: AsyncSession = Depends(get_session)
):
    """Статистика по выручке (только для админов)"""
    if not check_admin(user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Общая выручка
    result = await session.execute(
        select(func.sum(Payment.amount)).where(Payment.status == 'succeeded')
    )
    total_revenue = float(result.scalar() or 0)
    
    # Выручка за сегодня
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    result = await session.execute(
        select(func.sum(Payment.amount))
        .where(Payment.status == 'succeeded', Payment.created_at >= today)
    )
    revenue_today = float(result.scalar() or 0)
    
    # Выручка за неделю
    week_ago = datetime.now() - timedelta(days=7)
    result = await session.execute(
        select(func.sum(Payment.amount))
        .where(Payment.status == 'succeeded', Payment.created_at >= week_ago)
    )
    revenue_week = float(result.scalar() or 0)
    
    # Выручка за месяц
    month_ago = datetime.now() - timedelta(days=30)
    result = await session.execute(
        select(func.sum(Payment.amount))
        .where(Payment.status == 'succeeded', Payment.created_at >= month_ago)
    )
    revenue_month = float(result.scalar() or 0)
    
    # Всего платежей
    result = await session.execute(select(func.count(Payment.id)))
    total_payments = result.scalar() or 0
    
    # Успешных платежей
    result = await session.execute(
        select(func.count(Payment.id)).where(Payment.status == 'succeeded')
    )
    successful_payments = result.scalar() or 0
    
    return RevenueStatsResponse(
        total_revenue=total_revenue,
        revenue_today=revenue_today,
        revenue_week=revenue_week,
        revenue_month=revenue_month,
        total_payments=total_payments,
        successful_payments=successful_payments
    )


@router.get("/funnel", response_model=ConversionFunnelResponse)
async def get_conversion_funnel(
    user: dict = Depends(get_telegram_user),
    session: AsyncSession = Depends(get_session)
):
    """Воронка конверсии (только для админов)"""
    if not check_admin(user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Посетители (все пользователи)
    result = await session.execute(select(func.count(User.id)))
    visitors = result.scalar() or 0
    
    # Зарегистрированные (все пользователи, так как регистрация обязательна)
    registered = visitors
    
    # Купившие (пользователи с хотя бы одним платежом)
    result = await session.execute(
        select(func.count(func.distinct(Payment.user_id)))
        .where(Payment.status == 'succeeded')
    )
    purchased = result.scalar() or 0
    
    # Начавшие обучение (пользователи с прогрессом)
    result = await session.execute(
        select(func.count(func.distinct(UserProgress.user_id)))
    )
    started_learning = result.scalar() or 0
    
    # Завершившие курс (пользователи с сертификатами)
    result = await session.execute(
        select(func.count(func.distinct(Certificate.user_id)))
    )
    completed_course = result.scalar() or 0
    
    return ConversionFunnelResponse(
        visitors=visitors,
        registered=registered,
        purchased=purchased,
        started_learning=started_learning,
        completed_course=completed_course
    )


@router.get("/courses", response_model=List[CourseAnalyticsResponse])
async def get_courses_analytics(
    user: dict = Depends(get_telegram_user),
    session: AsyncSession = Depends(get_session)
):
    """Аналитика по каждому курсу (только для админов)"""
    if not check_admin(user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Получаем все курсы
    result = await session.execute(select(Course))
    courses = result.scalars().all()
    
    analytics = []
    for course in courses:
        # Количество записей
        result = await session.execute(
            select(func.count(UserCourse.id))
            .where(UserCourse.course_id == course.id)
        )
        enrollments = result.scalar() or 0
        
        # Количество завершений
        result = await session.execute(
            select(func.count(UserCourse.id))
            .where(UserCourse.course_id == course.id, UserCourse.is_completed == True)
        )
        completions = result.scalar() or 0
        
        # Процент завершения
        completion_rate = (completions / enrollments * 100) if enrollments > 0 else 0
        
        # Средний прогресс
        result = await session.execute(
            select(
                func.avg(
                    func.cast(
                        func.count(UserProgress.id),
                        func.Float
                    ) / func.cast(
                        func.count(func.distinct(Lesson.id)),
                        func.Float
                    ) * 100
                )
            )
            .select_from(UserCourse)
            .join(UserProgress, UserProgress.user_id == UserCourse.user_id)
            .join(Lesson, Lesson.course_id == course.id)
            .where(UserCourse.course_id == course.id)
            .group_by(UserCourse.user_id)
        )
        avg_progress = float(result.scalar() or 0)
        
        # Выручка от курса
        result = await session.execute(
            select(func.sum(Payment.amount))
            .join(UserCourse, UserCourse.user_id == Payment.user_id)
            .where(
                UserCourse.course_id == course.id,
                Payment.status == 'succeeded'
            )
        )
        revenue = float(result.scalar() or 0)
        
        analytics.append(CourseAnalyticsResponse(
            course_id=course.id,
            course_title=course.title,
            enrollments=enrollments,
            completions=completions,
            completion_rate=round(completion_rate, 2),
            average_progress=round(avg_progress, 2),
            revenue=revenue
        ))
    
    return analytics


@router.get("/daily", response_model=List[DailyStatsResponse])
async def get_daily_stats(
    days: int = 30,
    user: dict = Depends(get_telegram_user),
    session: AsyncSession = Depends(get_session)
):
    """Статистика по дням (только для админов)"""
    if not check_admin(user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    daily_stats = []
    for i in range(days):
        date = (datetime.now() - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
        next_date = date + timedelta(days=1)
        
        # Новые пользователи
        result = await session.execute(
            select(func.count(User.id))
            .where(User.created_at >= date, User.created_at < next_date)
        )
        new_users = result.scalar() or 0
        
        # Новые записи на курсы
        result = await session.execute(
            select(func.count(UserCourse.id))
            .where(UserCourse.created_at >= date, UserCourse.created_at < next_date)
        )
        new_enrollments = result.scalar() or 0
        
        # Завершенные уроки
        result = await session.execute(
            select(func.count(UserProgress.id))
            .where(UserProgress.completed_at >= date, UserProgress.completed_at < next_date)
        )
        completed_lessons = result.scalar() or 0
        
        # Выручка
        result = await session.execute(
            select(func.sum(Payment.amount))
            .where(
                Payment.status == 'succeeded',
                Payment.created_at >= date,
                Payment.created_at < next_date
            )
        )
        revenue = float(result.scalar() or 0)
        
        daily_stats.append(DailyStatsResponse(
            date=date.strftime('%Y-%m-%d'),
            new_users=new_users,
            new_enrollments=new_enrollments,
            completed_lessons=completed_lessons,
            revenue=revenue
        ))
    
    # Сортируем по дате (от старых к новым)
    daily_stats.reverse()
    return daily_stats

