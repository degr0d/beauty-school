"""
Точка входа приложения
Запускает все сервисы: Telegram бот, FastAPI, Админ-бот
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from backend.config import settings
from backend.bot.bot import setup_bot_handlers
from backend.admin_bot.bot import setup_admin_bot_handlers
from backend.webapp.app import create_app
from backend.database.database import init_db


# Настройка логирования
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def start_telegram_bot():
    """
    Запускает основной Telegram-бот
    """
    logger.info("Запуск основного Telegram-бота...")
    
    # Создаём бота и диспетчер
    bot = Bot(token=settings.BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Регистрируем обработчики
    setup_bot_handlers(dp)
    
    # Удаляем webhook (если был) и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


async def start_admin_bot():
    """
    Запускает админ-бот
    """
    logger.info("Запуск админ-бота...")
    
    bot = Bot(token=settings.ADMIN_BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Регистрируем обработчики админ-бота
    setup_admin_bot_handlers(dp)
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


async def start_fastapi():
    """
    Запускает FastAPI сервер
    """
    import uvicorn
    
    logger.info(f"Запуск FastAPI на порту {settings.API_PORT}...")
    
    app = create_app()
    
    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=settings.API_PORT,
        log_level=settings.LOG_LEVEL.lower()
    )
    server = uvicorn.Server(config)
    await server.serve()


async def main():
    """
    Главная функция: инициализирует БД и запускает все сервисы
    """
    logger.info("=" * 50)
    logger.info("Beauty School Backend - Запуск")
    logger.info("=" * 50)
    
    # Инициализация базы данных
    logger.info("Инициализация базы данных...")
    await init_db()
    logger.info("База данных готова")
    
    # Запускаем все сервисы параллельно
    await asyncio.gather(
        start_telegram_bot(),
        start_admin_bot(),
        start_fastapi()
    )


if __name__ == "__main__":
    """
    Запуск приложения:
    python backend/main.py
    """
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки (Ctrl+C)")
        logger.info("Завершение работы...")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)


# ========================================
# АЛЬТЕРНАТИВНЫЙ ЗАПУСК (отдельные процессы)
# ========================================
# Если нужно запускать сервисы отдельно:
#
# 1. Только бот:
#    asyncio.run(start_telegram_bot())
#
# 2. Только FastAPI:
#    uvicorn backend.main:app --reload
#
# 3. Только админ-бот:
#    asyncio.run(start_admin_bot())

