"""
Инициализация и настройка основного Telegram-бота
"""

from aiogram import Dispatcher
from backend.bot.handlers import start, registration, webapp, commands
from backend.admin_bot.bot import setup_admin_bot_handlers


def setup_bot_handlers(dp: Dispatcher):
    """
    Регистрирует все обработчики бота
    
    Args:
        dp: Диспетчер aiogram
    """
    # Порядок важен! Более специфичные обработчики должны быть выше
    
    # 1. Команда /start (обычный бот) - должна быть ПЕРЕД админ-ботом
    # чтобы не-админы получили обычное приветствие
    dp.include_router(start.router)
    
    # 2. Админ-бот (обрабатывает /start для админов, но только если они админы)
    setup_admin_bot_handlers(dp)
    
    # 3. Команды (должны быть после /start)
    dp.include_router(commands.router)
    
    # 4. Процесс регистрации (FSM)
    dp.include_router(registration.router)
    
    # 5. Запуск Mini App
    dp.include_router(webapp.router)


# ========================================
# Пример структуры обработчиков:
# ========================================
# /start -> handlers/start.py
#   ├─ Приветствие
#   ├─ Кнопка "Присоединиться"
#   └─ Проверка: уже зарегистрирован?
#
# Регистрация -> handlers/registration.py
#   ├─ Согласие на обработку данных
#   ├─ Запрос ФИО (FSM: WAITING_FULLNAME)
#   ├─ Запрос телефона (FSM: WAITING_PHONE)
#   └─ Сохранение в БД
#
# Mini App -> handlers/webapp.py
#   └─ Кнопка "Открыть приложение"

