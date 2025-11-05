"""
Запуск ПОЛНОГО бота с регистрацией и FSM
Только основной бот (без админ-бота и FastAPI)
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from backend.config import settings
from backend.bot.bot import setup_bot_handlers
from backend.database.database import init_db

# Загружаем .env
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """
    Главная функция: инициализирует БД и запускает бота
    """
    logger.info("=" * 60)
    logger.info("Beauty School Bot - Запуск с полной регистрацией")
    logger.info("=" * 60)
    
    # Инициализация базы данных
    logger.info("Инициализация базы данных...")
    await init_db()
    logger.info("✅ База данных готова")
    
    # Создаём бота и диспетчер
    logger.info("Создание бота...")
    bot = Bot(token=settings.BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Регистрируем обработчики
    logger.info("Регистрация обработчиков...")
    setup_bot_handlers(dp)
    logger.info("✅ Обработчики зарегистрированы")
    
    # Получаем информацию о боте
    me = await bot.get_me()
    logger.info(f"✅ Бот запущен: @{me.username}")
    logger.info(f"   ID: {me.id}")
    logger.info(f"   Имя: {me.first_name}")
    
    logger.info("=" * 60)
    logger.info("🚀 Бот готов к работе!")
    logger.info("   Открой Telegram и напиши боту /start")
    logger.info("=" * 60)
    
    # Удаляем webhook и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n" + "=" * 60)
        logger.info("⛔ Получен сигнал остановки (Ctrl+C)")
        logger.info("=" * 60)
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}", exc_info=True)

