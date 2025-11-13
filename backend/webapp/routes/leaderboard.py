"""
API эндпоинты для лидбордов (топ пользователей)
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from backend.database import get_session, User, UserCourse, UserProgress
from backend.webapp.middleware import get_telegram_user

router = APIRouter()


# ========================================
# Схемы ответов
# ========================================
class LeaderboardEntry(BaseModel):
    position: int
    user_id: int
    full_name: str
    points: int
    completed_courses: int
    completed_lessons: int

    class Config:
        from_attributes = True


class MyPositionResponse(BaseModel):
    position: int
    points: int
    completed_courses: int
    completed_lessons: int
    total_users: int


# ========================================
# Эндпоинты
# ========================================
@router.get("", response_model=List[LeaderboardEntry])
@router.get("/", response_model=List[LeaderboardEntry])
async def get_leaderboard(
    limit: int = Query(default=10, ge=1, le=100),
    session: AsyncSession = Depends(get_session)
):
    """
    Получить топ пользователей по баллам
    
    Параметры:
    - limit: Количество пользователей (1-100, по умолчанию 10)
    """
    # Получаем всех активных пользователей
    users_result = await session.execute(
        select(User).where(User.is_active == True).order_by(desc(User.points))
    )
    all_users = users_result.scalars().all()
    
    # Для каждого пользователя считаем статистику
    leaderboard_data = []
    for user in all_users:
        # Считаем завершенные курсы
        courses_result = await session.execute(
            select(func.count(UserCourse.id))
            .where((UserCourse.user_id == user.id) & (UserCourse.is_completed == True))
        )
        completed_courses = courses_result.scalar() or 0
        
        # Считаем завершенные уроки
        lessons_result = await session.execute(
            select(func.count(UserProgress.id))
            .where((UserProgress.user_id == user.id) & (UserProgress.completed == True))
        )
        completed_lessons = lessons_result.scalar() or 0
        
        leaderboard_data.append({
            'user_id': user.id,
            'full_name': user.full_name or "Без имени",
            'points': user.points or 0,
            'completed_courses': completed_courses,
            'completed_lessons': completed_lessons
        })
    
    # Сортируем: баллы → курсы → уроки
    leaderboard_data.sort(
        key=lambda x: (x['points'], x['completed_courses'], x['completed_lessons']),
        reverse=True
    )
    
    # Берем топ N
    leaderboard_data = leaderboard_data[:limit]
    
    # Формируем ответ
    leaderboard = []
    for position, data in enumerate(leaderboard_data, start=1):
        leaderboard.append(LeaderboardEntry(
            position=position,
            user_id=data['user_id'],
            full_name=data['full_name'],
            points=data['points'],
            completed_courses=data['completed_courses'],
            completed_lessons=data['completed_lessons']
        ))
    
    return leaderboard


@router.get("/courses", response_model=List[LeaderboardEntry])
async def get_leaderboard_by_courses(
    limit: int = Query(default=10, ge=1, le=100),
    session: AsyncSession = Depends(get_session)
):
    """
    Получить топ пользователей по завершенным курсам
    
    Параметры:
    - limit: Количество пользователей (1-100, по умолчанию 10)
    """
    # Получаем всех активных пользователей
    users_result = await session.execute(
        select(User).where(User.is_active == True)
    )
    all_users = users_result.scalars().all()
    
    # Для каждого пользователя считаем статистику
    leaderboard_data = []
    for user in all_users:
        # Считаем завершенные курсы
        courses_result = await session.execute(
            select(func.count(UserCourse.id))
            .where((UserCourse.user_id == user.id) & (UserCourse.is_completed == True))
        )
        completed_courses = courses_result.scalar() or 0
        
        # Пропускаем пользователей без завершенных курсов
        if completed_courses == 0:
            continue
        
        # Считаем завершенные уроки
        lessons_result = await session.execute(
            select(func.count(UserProgress.id))
            .where((UserProgress.user_id == user.id) & (UserProgress.completed == True))
        )
        completed_lessons = lessons_result.scalar() or 0
        
        leaderboard_data.append({
            'user_id': user.id,
            'full_name': user.full_name or "Без имени",
            'points': user.points or 0,
            'completed_courses': completed_courses,
            'completed_lessons': completed_lessons
        })
    
    # Сортируем: курсы → баллы → уроки
    leaderboard_data.sort(
        key=lambda x: (x['completed_courses'], x['points'], x['completed_lessons']),
        reverse=True
    )
    
    # Берем топ N
    leaderboard_data = leaderboard_data[:limit]
    
    # Формируем ответ
    leaderboard = []
    for position, data in enumerate(leaderboard_data, start=1):
        leaderboard.append(LeaderboardEntry(
            position=position,
            user_id=data['user_id'],
            full_name=data['full_name'],
            points=data['points'],
            completed_courses=data['completed_courses'],
            completed_lessons=data['completed_lessons']
        ))
    
    return leaderboard


@router.get("/my-position", response_model=MyPositionResponse)
async def get_my_position(
    user: dict = Depends(get_telegram_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Получить позицию текущего пользователя в лидборде
    """
    # Преобразуем telegram_id в int
    telegram_id_raw = user["id"]
    telegram_id = int(telegram_id_raw) if telegram_id_raw else None
    
    if not telegram_id:
        raise HTTPException(status_code=400, detail="Invalid telegram_id")
    
    # Получаем пользователя
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    db_user = result.scalar_one_or_none()
    
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Получаем статистику пользователя
    result = await session.execute(
        select(
            func.count(UserCourse.id.distinct()).label('completed_courses')
        )
        .where((UserCourse.user_id == db_user.id) & (UserCourse.is_completed == True))
    )
    completed_courses = result.scalar() or 0
    
    result = await session.execute(
        select(
            func.count(UserProgress.id.distinct()).label('completed_lessons')
        )
        .where((UserProgress.user_id == db_user.id) & (UserProgress.completed == True))
    )
    completed_lessons = result.scalar() or 0
    
    # Подсчитываем позицию пользователя
    # Считаем сколько пользователей имеют больше баллов или равные баллы но больше курсов/уроков
    query = (
        select(func.count(User.id))
        .where(
            (User.is_active == True) &
            (
                (User.points > db_user.points) |
                (
                    (User.points == db_user.points) &
                    (
                        (select(func.count(UserCourse.id.distinct()))
                         .where((UserCourse.user_id == User.id) & (UserCourse.is_completed == True))
                         .as_scalar()) > completed_courses
                    )
                ) |
                (
                    (User.points == db_user.points) &
                    (
                        (select(func.count(UserCourse.id.distinct()))
                         .where((UserCourse.user_id == User.id) & (UserCourse.is_completed == True))
                         .as_scalar()) == completed_courses
                    ) &
                    (
                        (select(func.count(UserProgress.id.distinct()))
                         .where((UserProgress.user_id == User.id) & (UserProgress.completed == True))
                         .as_scalar()) > completed_lessons
                    )
                )
            )
        )
    )
    
    result = await session.execute(query)
    position = (result.scalar() or 0) + 1
    
    # Получаем общее количество активных пользователей
    result = await session.execute(
        select(func.count(User.id)).where(User.is_active == True)
    )
    total_users = result.scalar() or 0
    
    return MyPositionResponse(
        position=position,
        points=db_user.points or 0,
        completed_courses=completed_courses,
        completed_lessons=completed_lessons,
        total_users=total_users
    )

