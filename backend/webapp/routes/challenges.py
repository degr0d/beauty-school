"""
API эндпоинты для челленджей
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from datetime import datetime

from backend.database import get_session, Challenge, UserChallenge, User, UserProgress, UserCourse
from backend.webapp.middleware import get_telegram_user
from backend.services.gamification import add_points_to_user
from backend.services.notifications import send_notification

router = APIRouter()


# ========================================
# Схемы ответов
# ========================================
class ChallengeResponse(BaseModel):
    id: int
    title: str
    description: str
    icon_url: Optional[str]
    points_reward: int
    condition_type: str
    condition_value: int
    start_date: Optional[str]
    end_date: Optional[str]
    is_active: bool
    user_progress: Optional[int] = None
    user_completed: bool = False
    user_joined: bool = False

    class Config:
        from_attributes = True


class ChallengeDetailResponse(ChallengeResponse):
    """Детальная информация о челлендже"""
    pass


# ========================================
# Эндпоинты
# ========================================
@router.get("", response_model=List[ChallengeResponse])
@router.get("/", response_model=List[ChallengeResponse])
async def get_challenges(
    user: Optional[dict] = Depends(get_telegram_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Получить список активных челленджей
    
    Если пользователь авторизован - показывает прогресс участия
    """
    # Получаем активные челленджи
    query = select(Challenge).where(Challenge.is_active == True)
    
    # Фильтруем по датам (если указаны)
    now = datetime.now()
    query = query.where(
        (Challenge.start_date.is_(None) | (Challenge.start_date <= now)) &
        (Challenge.end_date.is_(None) | (Challenge.end_date >= now))
    )
    
    result = await session.execute(query.order_by(Challenge.created_at.desc()))
    challenges = result.scalars().all()
    
    # Если пользователь авторизован - получаем его прогресс
    user_id = None
    user_challenges_map = {}
    
    if user:
        telegram_id_raw = user["id"]
        telegram_id = int(telegram_id_raw) if telegram_id_raw else None
        
        if telegram_id:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            db_user = result.scalar_one_or_none()
            
            if db_user:
                user_id = db_user.id
                
                # Получаем участие пользователя в челленджах
                result = await session.execute(
                    select(UserChallenge).where(UserChallenge.user_id == db_user.id)
                )
                user_challenges = result.scalars().all()
                
                for uc in user_challenges:
                    user_challenges_map[uc.challenge_id] = {
                        "progress": uc.progress,
                        "completed": uc.is_completed,
                        "joined": True
                    }
    
    # Формируем ответ
    challenges_list = []
    for challenge in challenges:
        user_data = user_challenges_map.get(challenge.id, {})
        
        challenges_list.append(ChallengeResponse(
            id=challenge.id,
            title=challenge.title,
            description=challenge.description,
            icon_url=challenge.icon_url,
            points_reward=challenge.points_reward,
            condition_type=challenge.condition_type,
            condition_value=challenge.condition_value,
            start_date=challenge.start_date.isoformat() if challenge.start_date else None,
            end_date=challenge.end_date.isoformat() if challenge.end_date else None,
            is_active=challenge.is_active,
            user_progress=user_data.get("progress", 0) if user_data else None,
            user_completed=user_data.get("completed", False) if user_data else False,
            user_joined=user_data.get("joined", False) if user_data else False
        ))
    
    return challenges_list


@router.get("/{challenge_id}", response_model=ChallengeDetailResponse)
async def get_challenge(
    challenge_id: int,
    user: Optional[dict] = Depends(get_telegram_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Получить детали челленджа
    """
    result = await session.execute(
        select(Challenge).where(Challenge.id == challenge_id)
    )
    challenge = result.scalar_one_or_none()
    
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    # Получаем прогресс пользователя
    user_progress = None
    user_completed = False
    user_joined = False
    
    if user:
        telegram_id_raw = user["id"]
        telegram_id = int(telegram_id_raw) if telegram_id_raw else None
        
        if telegram_id:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            db_user = result.scalar_one_or_none()
            
            if db_user:
                result = await session.execute(
                    select(UserChallenge).where(
                        UserChallenge.user_id == db_user.id,
                        UserChallenge.challenge_id == challenge_id
                    )
                )
                user_challenge = result.scalar_one_or_none()
                
                if user_challenge:
                    user_progress = user_challenge.progress
                    user_completed = user_challenge.is_completed
                    user_joined = True
    
    return ChallengeDetailResponse(
        id=challenge.id,
        title=challenge.title,
        description=challenge.description,
        icon_url=challenge.icon_url,
        points_reward=challenge.points_reward,
        condition_type=challenge.condition_type,
        condition_value=challenge.condition_value,
        start_date=challenge.start_date.isoformat() if challenge.start_date else None,
        end_date=challenge.end_date.isoformat() if challenge.end_date else None,
        is_active=challenge.is_active,
        user_progress=user_progress,
        user_completed=user_completed,
        user_joined=user_joined
    )


@router.post("/{challenge_id}/join")
async def join_challenge(
    challenge_id: int,
    user: dict = Depends(get_telegram_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Присоединиться к челленджу
    """
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
    
    # Получаем челлендж
    result = await session.execute(
        select(Challenge).where(Challenge.id == challenge_id)
    )
    challenge = result.scalar_one_or_none()
    
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    if not challenge.is_active:
        raise HTTPException(status_code=400, detail="Challenge is not active")
    
    # Проверяем, не присоединился ли уже
    result = await session.execute(
        select(UserChallenge).where(
            UserChallenge.user_id == db_user.id,
            UserChallenge.challenge_id == challenge_id
        )
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        return {"message": "Вы уже участвуете в этом челлендже", "joined": True}
    
    # Присоединяемся к челленджу
    user_challenge = UserChallenge(
        user_id=db_user.id,
        challenge_id=challenge_id,
        progress=0,
        is_completed=False
    )
    session.add(user_challenge)
    await session.commit()
    await session.refresh(user_challenge)
    
    # Отправляем уведомление
    try:
        await send_notification(
            db_user.telegram_id,
            f"🎯 <b>Вы присоединились к челленджу!</b>\n\n"
            f"<b>{challenge.title}</b>\n"
            f"{challenge.description}\n\n"
            f"💎 Награда: {challenge.points_reward} баллов"
        )
    except Exception as e:
        print(f"⚠️ Ошибка отправки уведомления: {e}")
    
    return {"message": "Вы успешно присоединились к челленджу", "joined": True}


@router.get("/my", response_model=List[ChallengeResponse])
async def get_my_challenges(
    user: dict = Depends(get_telegram_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Получить челленджи, в которых участвует пользователь
    """
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
    
    # Получаем челленджи пользователя
    result = await session.execute(
        select(UserChallenge, Challenge)
        .join(Challenge, UserChallenge.challenge_id == Challenge.id)
        .where(UserChallenge.user_id == db_user.id)
        .order_by(UserChallenge.joined_at.desc())
    )
    user_challenges = result.all()
    
    challenges_list = []
    for uc, challenge in user_challenges:
        challenges_list.append(ChallengeResponse(
            id=challenge.id,
            title=challenge.title,
            description=challenge.description,
            icon_url=challenge.icon_url,
            points_reward=challenge.points_reward,
            condition_type=challenge.condition_type,
            condition_value=challenge.condition_value,
            start_date=challenge.start_date.isoformat() if challenge.start_date else None,
            end_date=challenge.end_date.isoformat() if challenge.end_date else None,
            is_active=challenge.is_active,
            user_progress=uc.progress,
            user_completed=uc.is_completed,
            user_joined=True
        ))
    
    return challenges_list


