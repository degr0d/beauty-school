"""
Запуск БОТА + API одновременно
Для полноценной работы системы
"""

import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import uvicorn
from dotenv import load_dotenv

from backend.config import settings
from backend.bot.bot import setup_bot_handlers
from backend.database.database import init_db, create_engine_and_session
from backend.webapp.app import create_app

# Загружаем .env
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def start_bot():
    """
    Запускает Telegram бота
    """
    logger.info("Запуск Telegram бота...")
    
    bot = Bot(token=settings.BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Регистрируем обработчики
    setup_bot_handlers(dp)
    
    # Получаем информацию о боте
    try:
        me = await bot.get_me()
        logger.info(f"✅ Бот запущен: @{me.username}")
    except Exception as e:
        logger.error("=" * 60)
        logger.error("❌ ОШИБКА ПОДКЛЮЧЕНИЯ К TELEGRAM")
        logger.error("=" * 60)
        logger.error(f"Ошибка: {e}")
        logger.error("")
        logger.error("Возможные причины:")
        logger.error("1. VPN не включен (Telegram API заблокирован)")
        logger.error("2. Неверный BOT_TOKEN в .env файле")
        logger.error("3. Бот удален или деактивирован в @BotFather")
        logger.error("")
        logger.error("Что делать:")
        logger.error("- Включите VPN и попробуйте снова")
        logger.error("- Проверьте токен в @BotFather (/token)")
        logger.error("- Обновите BOT_TOKEN в .env файле")
        logger.error("")
        logger.error("⚠️ API продолжит работать без бота")
        logger.error("=" * 60)
        await bot.session.close()
        # Не поднимаем исключение - пусть API работает
        return
    
    # Запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


async def start_api():
    """
    Запускает FastAPI сервер
    """
    logger.info(f"Запуск FastAPI на порту {settings.API_PORT}...")
    
    app = create_app()
    
    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=settings.API_PORT,
        log_level="info"
    )
    server = uvicorn.Server(config)
    
    logger.info(f"✅ API доступен на http://localhost:{settings.API_PORT}")
    logger.info(f"   Docs: http://localhost:{settings.API_PORT}/api/docs")
    
    await server.serve()


async def main():
    """
    Главная функция: инициализирует БД и запускает все сервисы
    """
    logger.info("=" * 60)
    logger.info("Beauty School - Полный запуск (Бот + API)")
    logger.info("=" * 60)
    
    # Инициализация базы данных
    # Сначала создаем engine и session factory
    logger.info("Инициализация базы данных...")
    create_engine_and_session()
    # Теперь можем инициализировать БД (создать таблицы)
    try:
        await init_db()
        logger.info("✅ База данных готова")
    except Exception as db_error:
        logger.warning(f"⚠️ Ошибка инициализации БД: {db_error}")
        logger.warning("💡 Продолжаем запуск - таблицы могут быть созданы через startup_event")
    
    logger.info("=" * 60)
    logger.info("🚀 Запуск сервисов...")
    logger.info("=" * 60)
    
    # Запускаем API и бота параллельно
    # Если бот не запустится - API продолжит работать
    bot_task = None
    
    # В режиме разработки можно отключить бота, если он уже запущен на сервере
    # Установите SKIP_BOT=true в .env чтобы пропустить запуск бота локально
    skip_bot = os.getenv("SKIP_BOT", "false").lower() == "true"
    
    if skip_bot:
        logger.info("⏭️  Пропуск запуска бота (SKIP_BOT=true)")
        logger.info("💡 Бот уже запущен на сервере, локально не нужен")
    else:
        try:
            # Создаем задачу для бота (не блокируем API если бот упадет)
            bot_task = asyncio.create_task(start_bot())
            logger.info("Задача бота создана")
        except Exception as bot_error:
            logger.warning("⚠️ Не удалось создать задачу бота, но API запустится")
            logger.warning(f"Ошибка: {bot_error}")
    
    # Запускаем API (всегда должен работать)
    try:
        await start_api()
    except Exception as api_error:
        logger.error(f"❌ API не смог запуститься: {api_error}")
        # Если API упал, отменяем и бота
        if bot_task and not bot_task.done():
            bot_task.cancel()
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n" + "=" * 60)
        logger.info("⛔ Получен сигнал остановки (Ctrl+C)")
        logger.info("=" * 60)
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}", exc_info=True)

