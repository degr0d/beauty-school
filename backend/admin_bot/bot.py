"""
Инициализация и настройка админ-бота
"""

from aiogram import Dispatcher
from backend.admin_bot.handlers import analytics, users_mgmt, courses_mgmt, support


def setup_admin_bot_handlers(dp: Dispatcher):
    """
    Регистрирует обработчики админ-бота
    
    Args:
        dp: Диспетчер aiogram
    """
    # Порядок регистрации обработчиков
    
    # 1. Аналитика
    dp.include_router(analytics.router)
    
    # 2. Управление пользователями
    dp.include_router(users_mgmt.router)
    
    # 3. Управление курсами
    dp.include_router(courses_mgmt.router)
    
    # 4. Поддержка
    dp.include_router(support.router)


# ========================================
# Структура админ-бота:
# ========================================
# /start - Приветствие админа
# /stats - Общая статистика
# /users - Управление пользователями
# /courses - Управление курсами
# /analytics - Детальная аналитика

