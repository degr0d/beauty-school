"""
Модуль работы с базой данных
"""

from backend.database.database import get_engine, get_async_session, Base, get_session, engine as _engine_func, async_session as _async_session_func

# Для обратной совместимости - экспортируем функции
engine = _engine_func
async_session = _async_session_func
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
]

