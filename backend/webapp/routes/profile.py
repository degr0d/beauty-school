"""
API эндпоинты для профиля пользователя
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_session, User
from backend.webapp.schemas import ProfileResponse, ProfileUpdateRequest
from backend.webapp.middleware import get_telegram_user

router = APIRouter()


@router.get("/", response_model=ProfileResponse)
async def get_profile(
    user: dict = Depends(get_telegram_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Получить профиль текущего пользователя
    """
    telegram_id = user["id"]
    print(f"🔍 [Profile] Запрос профиля для telegram_id={telegram_id}")
    
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    db_user = result.scalar_one_or_none()
    
    if not db_user:
        print(f"❌ [Profile] Пользователь не найден: telegram_id={telegram_id}")
        # Проверяем какие пользователи есть в БД (для диагностики)
        all_users = await session.execute(select(User.telegram_id))
        existing_ids = [u[0] for u in all_users.fetchall()]
        print(f"   Зарегистрированные telegram_id: {existing_ids}")
        raise HTTPException(status_code=404, detail="User not found")
    
    print(f"✅ [Profile] Профиль найден: {db_user.full_name} (telegram_id={db_user.telegram_id})")
    
    return ProfileResponse(
        id=db_user.id,
        telegram_id=db_user.telegram_id,
        username=db_user.username,
        full_name=db_user.full_name,
        phone=db_user.phone,
        city=db_user.city,
        points=db_user.points,
        created_at=db_user.created_at
    )


@router.put("/", response_model=ProfileResponse)
async def update_profile(
    profile_data: ProfileUpdateRequest,
    user: dict = Depends(get_telegram_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Обновить профиль пользователя
    """
    telegram_id = user["id"]
    
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    db_user = result.scalar_one_or_none()
    
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Обновляем поля
    if profile_data.full_name:
        db_user.full_name = profile_data.full_name
    if profile_data.phone:
        db_user.phone = profile_data.phone
    if profile_data.city:
        db_user.city = profile_data.city
    
    await session.commit()
    await session.refresh(db_user)
    
    return ProfileResponse(
        id=db_user.id,
        telegram_id=db_user.telegram_id,
        username=db_user.username,
        full_name=db_user.full_name,
        phone=db_user.phone,
        city=db_user.city,
        points=db_user.points,
        created_at=db_user.created_at
    )


# ========================================
# Пример запроса:
# ========================================
# GET /api/profile
# PUT /api/profile
# Body: {"full_name": "Иванова Мария", "city": "Москва"}

