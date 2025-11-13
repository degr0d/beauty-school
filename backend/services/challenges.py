"""
Сервис для проверки и обновления прогресса челленджей
"""

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from backend.database.models import (
    User, UserChallenge, Challenge, UserProgress, UserCourse
)
from backend.services.gamification import add_points_to_user
from backend.services.notifications import send_notification


async def check_challenge_progress(
    session: AsyncSession,
    user_id: int,
    challenge_id: int
) -> bool:
    """
    Проверить прогресс пользователя в челлендже и обновить его
    
    Args:
        session: SQLAlchemy сессия
        user_id: ID пользователя
        challenge_id: ID челленджа
    
    Returns:
        True если челлендж только что был завершен
    """
    # Получаем участие пользователя в челлендже
    result = await session.execute(
        select(UserChallenge).where(
            UserChallenge.user_id == user_id,
            UserChallenge.challenge_id == challenge_id
        )
    )
    user_challenge = result.scalar_one_or_none()
    
    if not user_challenge or user_challenge.is_completed:
        return False
    
    # Получаем челлендж
    result = await session.execute(
        select(Challenge).where(Challenge.id == challenge_id)
    )
    challenge = result.scalar_one_or_none()
    
    if not challenge:
        return False
    
    # Вычисляем текущий прогресс в зависимости от типа условия
    current_progress = 0
    
    if challenge.condition_type == "complete_lessons":
        # Количество завершенных уроков
        result = await session.execute(
            select(func.count(UserProgress.id)).where(
                UserProgress.user_id == user_id,
                UserProgress.completed == True
            )
        )
        current_progress = result.scalar() or 0
    
    elif challenge.condition_type == "complete_courses":
        # Количество завершенных курсов
        result = await session.execute(
            select(func.count(UserCourse.id)).where(
                UserCourse.user_id == user_id,
                UserCourse.is_completed == True
            )
        )
        current_progress = result.scalar() or 0
    
    elif challenge.condition_type == "earn_points":
        # Количество заработанных баллов
        result = await session.execute(
            select(User.points).where(User.id == user_id)
        )
        current_progress = result.scalar() or 0
    
    # Обновляем прогресс
    user_challenge.progress = min(current_progress, challenge.condition_value)
    
    # Проверяем, выполнен ли челлендж
    if current_progress >= challenge.condition_value and not user_challenge.is_completed:
        user_challenge.is_completed = True
        user_challenge.completed_at = datetime.now()
        
        # Начисляем награду
        if challenge.points_reward > 0:
            await add_points_to_user(
                session,
                user_id,
                challenge.points_reward,
                f"Челлендж: {challenge.title}"
            )
        
        # Отправляем уведомление
        try:
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if user:
                await send_notification(
                    user.telegram_id,
                    f"🎉 <b>Челлендж выполнен!</b>\n\n"
                    f"🏆 <b>{challenge.title}</b>\n\n"
                    f"💎 +{challenge.points_reward} баллов"
                )
        except Exception as e:
            print(f"⚠️ Ошибка отправки уведомления о челлендже: {e}")
        
        await session.commit()
        return True
    
    await session.commit()
    return False


async def check_all_user_challenges(
    session: AsyncSession,
    user_id: int
) -> list[int]:
    """
    Проверить все активные челленджи пользователя
    
    Args:
        session: SQLAlchemy сессия
        user_id: ID пользователя
    
    Returns:
        Список ID завершенных челленджей
    """
    # Получаем активные челленджи пользователя
    result = await session.execute(
        select(UserChallenge, Challenge)
        .join(Challenge, UserChallenge.challenge_id == Challenge.id)
        .where(
            UserChallenge.user_id == user_id,
            UserChallenge.is_completed == False,
            Challenge.is_active == True
        )
    )
    user_challenges = result.all()
    
    completed_challenge_ids = []
    
    for uc, challenge in user_challenges:
        if await check_challenge_progress(session, user_id, challenge.id):
            completed_challenge_ids.append(challenge.id)
    
    return completed_challenge_ids

