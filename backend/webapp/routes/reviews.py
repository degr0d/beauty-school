"""
API эндпоинты для отзывов и рейтингов
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from backend.database import get_session, Review, Course, User
from backend.webapp.middleware import get_telegram_user

router = APIRouter()


# ========================================
# Схемы запросов и ответов
# ========================================
class ReviewCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Рейтинг от 1 до 5")
    comment: Optional[str] = Field(None, max_length=2000, description="Текст отзыва")


class ReviewResponse(BaseModel):
    id: int
    user_id: int
    user_name: str
    course_id: int
    rating: int
    comment: Optional[str]
    created_at: str
    updated_at: Optional[str]

    class Config:
        from_attributes = True


class CourseRatingResponse(BaseModel):
    course_id: int
    average_rating: float
    total_reviews: int
    rating_distribution: dict  # {1: count, 2: count, ...}


# ========================================
# Эндпоинты
# ========================================
@router.get("/course/{course_id}", response_model=List[ReviewResponse])
async def get_course_reviews(
    course_id: int,
    limit: int = 50,
    offset: int = 0,
    session: AsyncSession = Depends(get_session)
):
    """
    Получить отзывы по курсу
    """
    # Проверяем существование курса
    result = await session.execute(
        select(Course).where(Course.id == course_id)
    )
    course = result.scalar_one_or_none()
    
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Получаем отзывы с информацией о пользователях
    result = await session.execute(
        select(Review, User)
        .join(User, Review.user_id == User.id)
        .where(Review.course_id == course_id)
        .order_by(Review.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    reviews = result.all()
    
    reviews_list = []
    for review, user in reviews:
        reviews_list.append(ReviewResponse(
            id=review.id,
            user_id=review.user_id,
            user_name=user.full_name or "Пользователь",
            course_id=review.course_id,
            rating=review.rating,
            comment=review.comment,
            created_at=review.created_at.isoformat() if review.created_at else "",
            updated_at=review.updated_at.isoformat() if review.updated_at else None
        ))
    
    return reviews_list


@router.get("/course/{course_id}/rating", response_model=CourseRatingResponse)
async def get_course_rating(
    course_id: int,
    session: AsyncSession = Depends(get_session)
):
    """
    Получить рейтинг курса (средний рейтинг, количество отзывов, распределение)
    """
    # Проверяем существование курса
    result = await session.execute(
        select(Course).where(Course.id == course_id)
    )
    course = result.scalar_one_or_none()
    
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Получаем средний рейтинг и количество отзывов
    result = await session.execute(
        select(
            func.avg(Review.rating).label('avg_rating'),
            func.count(Review.id).label('total_reviews')
        )
        .where(Review.course_id == course_id)
    )
    stats = result.first()
    
    average_rating = float(stats.avg_rating) if stats.avg_rating else 0.0
    total_reviews = stats.total_reviews or 0
    
    # Получаем распределение рейтингов
    result = await session.execute(
        select(Review.rating, func.count(Review.id).label('count'))
        .where(Review.course_id == course_id)
        .group_by(Review.rating)
    )
    distribution_rows = result.all()
    
    rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for rating, count in distribution_rows:
        if 1 <= rating <= 5:
            rating_distribution[rating] = count
    
    return CourseRatingResponse(
        course_id=course_id,
        average_rating=round(average_rating, 2),
        total_reviews=total_reviews,
        rating_distribution=rating_distribution
    )


@router.post("/course/{course_id}", response_model=ReviewResponse)
async def create_review(
    course_id: int,
    review_data: ReviewCreate,
    user: dict = Depends(get_telegram_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Создать отзыв на курс
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
    
    # Проверяем, не оставил ли пользователь уже отзыв на этот курс
    result = await session.execute(
        select(Review).where(
            Review.user_id == db_user.id,
            Review.course_id == course_id
        )
    )
    existing_review = result.scalar_one_or_none()
    
    if existing_review:
        # Обновляем существующий отзыв
        existing_review.rating = review_data.rating
        existing_review.comment = review_data.comment
        await session.commit()
        await session.refresh(existing_review)
        
        return ReviewResponse(
            id=existing_review.id,
            user_id=existing_review.user_id,
            user_name=db_user.full_name or "Пользователь",
            course_id=existing_review.course_id,
            rating=existing_review.rating,
            comment=existing_review.comment,
            created_at=existing_review.created_at.isoformat() if existing_review.created_at else "",
            updated_at=existing_review.updated_at.isoformat() if existing_review.updated_at else None
        )
    
    # Создаем новый отзыв
    review = Review(
        user_id=db_user.id,
        course_id=course_id,
        rating=review_data.rating,
        comment=review_data.comment
    )
    session.add(review)
    await session.commit()
    await session.refresh(review)
    
    return ReviewResponse(
        id=review.id,
        user_id=review.user_id,
        user_name=db_user.full_name or "Пользователь",
        course_id=review.course_id,
        rating=review.rating,
        comment=review.comment,
        created_at=review.created_at.isoformat() if review.created_at else "",
        updated_at=review.updated_at.isoformat() if review.updated_at else None
    )


@router.delete("/{review_id}")
async def delete_review(
    review_id: int,
    user: dict = Depends(get_telegram_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Удалить свой отзыв
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
    
    # Получаем отзыв
    result = await session.execute(
        select(Review).where(Review.id == review_id)
    )
    review = result.scalar_one_or_none()
    
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    # Проверяем, что отзыв принадлежит пользователю
    if review.user_id != db_user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own reviews")
    
    # Удаляем отзыв
    await session.delete(review)
    await session.commit()
    
    return {"message": "Review deleted successfully"}


@router.get("/my", response_model=List[ReviewResponse])
async def get_my_reviews(
    user: dict = Depends(get_telegram_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Получить все отзывы текущего пользователя
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
    
    # Получаем отзывы пользователя
    result = await session.execute(
        select(Review)
        .where(Review.user_id == db_user.id)
        .order_by(Review.created_at.desc())
    )
    reviews = result.scalars().all()
    
    reviews_list = []
    for review in reviews:
        reviews_list.append(ReviewResponse(
            id=review.id,
            user_id=review.user_id,
            user_name=db_user.full_name or "Пользователь",
            course_id=review.course_id,
            rating=review.rating,
            comment=review.comment,
            created_at=review.created_at.isoformat() if review.created_at else "",
            updated_at=review.updated_at.isoformat() if review.updated_at else None
        ))
    
    return reviews_list

