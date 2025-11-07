"""
API эндпоинты для достижений (ачивок)
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from backend.database import get_session, Achievement, UserAchievement, User
from backend.webapp.middleware import get_telegram_user

router = APIRouter()


# ========================================
# Схемы ответов
# ========================================
class AchievementResponse(BaseModel):
    id: int
    title: str
    description: str
    icon_url: Optional[str]
    points: int
    condition_type: str
    condition_value: int
    earned: bool = False  # Получено ли пользователем
    earned_at: Optional[str] = None  # Дата получения

    class Config:
        from_attributes = True


class AchievementDetailResponse(AchievementResponse):
    """Детальная информация о достижении"""
    pass


# ========================================
# Эндпоинты
# ========================================
@router.get("/", response_model=List[AchievementResponse])
async def get_achievements(
    user: Optional[dict] = Depends(get_telegram_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Получить список всех достижений
    
    Если пользователь авторизован - показывает, какие достижения он получил
    """
    # Получаем все достижения
    result = await session.execute(select(Achievement).order_by(Achievement.points.desc()))
    all_achievements = result.scalars().all()
    
    # Если пользователь авторизован - проверяем полученные достижения
    earned_achievement_ids = set()
    earned_achievements_map = {}
    
    if user:
        # Преобразуем telegram_id в int
        telegram_id_raw = user["id"]
        telegram_id = int(telegram_id_raw) if telegram_id_raw else None
        
        if telegram_id:
            # Получаем пользователя
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            db_user = result.scalar_one_or_none()
            
            if db_user:
                # Получаем полученные достижения
                result = await session.execute(
                    select(UserAchievement).where(
                        UserAchievement.user_id == db_user.id
                    )
                )
                user_achievements = result.scalars().all()
                
                for ua in user_achievements:
                    earned_achievement_ids.add(ua.achievement_id)
                    earned_achievements_map[ua.achievement_id] = ua.earned_at.isoformat() if ua.earned_at else None
    
    # Формируем ответ
    achievements_list = []
    for achievement in all_achievements:
        earned = achievement.id in earned_achievement_ids
        achievements_list.append(AchievementResponse(
            id=achievement.id,
            title=achievement.title,
            description=achievement.description,
            icon_url=achievement.icon_url,
            points=achievement.points,
            condition_type=achievement.condition_type,
            condition_value=achievement.condition_value,
            earned=earned,
            earned_at=earned_achievements_map.get(achievement.id)
        ))
    
    return achievements_list


@router.get("/my", response_model=List[AchievementResponse])
async def get_my_achievements(
    user: dict = Depends(get_telegram_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Получить достижения текущего пользователя
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
    
    # Получаем полученные достижения пользователя
    result = await session.execute(
        select(UserAchievement, Achievement)
        .join(Achievement, UserAchievement.achievement_id == Achievement.id)
        .where(UserAchievement.user_id == db_user.id)
        .order_by(UserAchievement.earned_at.desc())
    )
    user_achievements = result.all()
    
    achievements_list = []
    for ua, achievement in user_achievements:
        achievements_list.append(AchievementResponse(
            id=achievement.id,
            title=achievement.title,
            description=achievement.description,
            icon_url=achievement.icon_url,
            points=achievement.points,
            condition_type=achievement.condition_type,
            condition_value=achievement.condition_value,
            earned=True,
            earned_at=ua.earned_at.isoformat() if ua.earned_at else None
        ))
    
    return achievements_list


@router.get("/{achievement_id}", response_model=AchievementDetailResponse)
async def get_achievement(
    achievement_id: int,
    user: Optional[dict] = Depends(get_telegram_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Получить детали конкретного достижения
    """
    # Получаем достижение
    result = await session.execute(
        select(Achievement).where(Achievement.id == achievement_id)
    )
    achievement = result.scalar_one_or_none()
    
    if not achievement:
        raise HTTPException(status_code=404, detail="Achievement not found")
    
    # Проверяем, получено ли пользователем
    earned = False
    earned_at = None
    
    if user:
        # Преобразуем telegram_id в int
        telegram_id_raw = user["id"]
        telegram_id = int(telegram_id_raw) if telegram_id_raw else None
        
        if telegram_id:
            # Получаем пользователя
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            db_user = result.scalar_one_or_none()
            
            if db_user:
                # Проверяем, получено ли достижение
                result = await session.execute(
                    select(UserAchievement).where(
                        UserAchievement.user_id == db_user.id,
                        UserAchievement.achievement_id == achievement_id
                    )
                )
                user_achievement = result.scalar_one_or_none()
                
                if user_achievement:
                    earned = True
                    earned_at = user_achievement.earned_at.isoformat() if user_achievement.earned_at else None
    
    return AchievementDetailResponse(
        id=achievement.id,
        title=achievement.title,
        description=achievement.description,
        icon_url=achievement.icon_url,
        points=achievement.points,
        condition_type=achievement.condition_type,
        condition_value=achievement.condition_value,
        earned=earned,
        earned_at=earned_at
    )

