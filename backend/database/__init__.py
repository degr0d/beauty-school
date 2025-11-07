"""
Модуль работы с базой данных
"""

from backend.database.database import get_engine, get_async_session, Base, get_session

# Для обратной совместимости - экспортируем функции
# Теперь engine и async_session - это функции, которые возвращают нужные объекты
def engine():
    """Для обратной совместимости - возвращает engine"""
    return get_engine()

def async_session():
    """Для обратной совместимости - возвращает фабрику сессий"""
    return get_async_session()
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

