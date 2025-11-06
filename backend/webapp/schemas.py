"""
Pydantic схемы для FastAPI
Request и Response модели
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ========================================
# Courses
# ========================================

class CourseResponse(BaseModel):
    """
    Схема для списка курсов
    """
    id: int
    title: str
    description: str
    category: str
    cover_image_url: Optional[str] = None
    is_top: bool
    price: float
    duration_hours: Optional[int] = None
    
    class Config:
        from_attributes = True


class LessonShortResponse(BaseModel):
    """
    Краткая информация об уроке (для списка в курсе)
    """
    id: int
    title: str
    order: int
    video_duration: Optional[int] = None
    is_free: bool


class CourseDetailResponse(BaseModel):
    """
    Детальная информация о курсе + список уроков
    """
    id: int
    title: str
    description: str
    full_description: Optional[str] = None
    category: str
    cover_image_url: Optional[str] = None
    is_top: bool
    price: float
    duration_hours: Optional[int] = None
    lessons: List[LessonShortResponse]


# ========================================
# Lessons
# ========================================

class LessonDetailResponse(BaseModel):
    """
    Детальная информация об уроке
    """
    id: int
    course_id: int
    title: str
    description: Optional[str] = None
    order: int
    video_url: Optional[str] = None
    video_duration: Optional[int] = None
    pdf_url: Optional[str] = None
    is_free: bool
    
    class Config:
        from_attributes = True


# ========================================
# Profile
# ========================================

class ProfileResponse(BaseModel):
    """
    Схема профиля пользователя
    """
    id: int
    telegram_id: int
    username: Optional[str] = None
    full_name: str
    phone: str
    email: Optional[str] = None
    city: Optional[str] = None
    points: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProfileUpdateRequest(BaseModel):
    """
    Схема для обновления профиля
    """
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    city: Optional[str] = None


# ========================================
# Progress
# ========================================

class ProgressResponse(BaseModel):
    """
    Схема прогресса по курсу
    """
    course_id: int
    course_title: str
    total_lessons: int
    completed_lessons: int
    progress_percent: float
    lessons: List[dict]


# ========================================
# Пример использования в эндпоинтах:
# ========================================
# @router.get("/courses", response_model=List[CourseResponse])
# async def get_courses():
#     ...

