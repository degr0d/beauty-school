"""
Модуль работы с базой данных
"""

from backend.database.database import get_engine, get_async_session, Base, get_session, engine, async_session
from backend.database.models import (
    User,
    Course,
    Lesson,
    UserCourse,
    UserProgress,
    Achievement,
    UserAchievement,
    Community,
    Payment,
    Certificate,
    Favorite,
    Review,
)

__all__ = [
    "engine",
    "async_session",
    "Base",
    "get_session",
    "User",
    "Course",
    "Lesson",
    "UserCourse",
    "UserProgress",
    "Achievement",
    "UserAchievement",
    "Community",
    "Payment",
    "Certificate",
    "Favorite",
    "Review",
]

