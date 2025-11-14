"""
API эндпоинты для избранного
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from backend.database import get_session, Favorite, Course, User
from backend.webapp.middleware import get_telegram_user
from backend.webapp.schemas import CourseResponse

router = APIRouter()


# ========================================
# Схемы ответов
# ========================================
class FavoriteResponse(BaseModel):
    course_id: int
    course: CourseResponse
    added_at: str

    class Config:
        from_attributes = True


# ========================================
# Эндпоинты
# ========================================
@router.get("", response_model=List[CourseResponse])
@router.get("/", response_model=List[CourseResponse])
async def get_favorites(
    user: dict = Depends(get_telegram_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Получить список избранных курсов пользователя
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
    
    # Получаем избранные курсы
    result = await session.execute(
        select(Favorite, Course)
        .join(Course, Favorite.course_id == Course.id)
        .where(Favorite.user_id == db_user.id)
        .order_by(Favorite.created_at.desc())
    )
    favorites = result.all()
    
    # Извлекаем курсы из кортежей (Favorite, Course)
    courses = [course for _, course in favorites]
    return courses


@router.post("/{course_id}")
async def add_to_favorites(
    course_id: int,
    user: dict = Depends(get_telegram_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Добавить курс в избранное
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
    
    # Проверяем существование курса
    result = await session.execute(
        select(Course).where(Course.id == course_id)
    )
    course = result.scalar_one_or_none()
    
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Проверяем, не добавлен ли уже в избранное
    result = await session.execute(
        select(Favorite).where(
            Favorite.user_id == db_user.id,
            Favorite.course_id == course_id
        )
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        return {"message": "Курс уже в избранном", "is_favorite": True}
    
    # Добавляем в избранное
    try:
        favorite = Favorite(
            user_id=db_user.id,
            course_id=course_id
        )
        session.add(favorite)
        await session.commit()
        await session.refresh(favorite)
        
        return {"message": "Курс добавлен в избранное", "is_favorite": True}
    except Exception as e:
        await session.rollback()
        # Если ошибка из-за дубликата - возвращаем успешный ответ
        if "unique constraint" in str(e).lower() or "duplicate" in str(e).lower():
            return {"message": "Курс уже в избранном", "is_favorite": True}
        # Иначе пробрасываем ошибку дальше
        raise HTTPException(status_code=500, detail=f"Ошибка при добавлении в избранное: {str(e)}")


@router.delete("/{course_id}")
async def remove_from_favorites(
    course_id: int,
    user: dict = Depends(get_telegram_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Удалить курс из избранного
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
    
    # Находим запись в избранном
    result = await session.execute(
        select(Favorite).where(
            Favorite.user_id == db_user.id,
            Favorite.course_id == course_id
        )
    )
    favorite = result.scalar_one_or_none()
    
    if not favorite:
        return {"message": "Курс не в избранном", "is_favorite": False}
    
    # Удаляем из избранного
    await session.delete(favorite)
    await session.commit()
    
    return {"message": "Курс удален из избранного", "is_favorite": False}


@router.get("/check/{course_id}")
async def check_favorite(
    course_id: int,
    user: dict = Depends(get_telegram_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Проверить, находится ли курс в избранном
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
    
    # Проверяем наличие в избранном
    result = await session.execute(
        select(Favorite).where(
            Favorite.user_id == db_user.id,
            Favorite.course_id == course_id
        )
    )
    favorite = result.scalar_one_or_none()
    
    return {"is_favorite": favorite is not None}

