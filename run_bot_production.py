"""
Запуск бота для продакшена (Railway)
Отдельный скрипт для запуска только бота
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
    logger.info("Beauty School Bot - Production (Railway)")
    logger.info("=" * 60)
    
    # Проверяем что BOT_TOKEN установлен
    if not settings.BOT_TOKEN:
        logger.error("=" * 60)
        logger.error("❌ ОШИБКА: BOT_TOKEN не установлен!")
        logger.error("=" * 60)
        logger.error("")
        logger.error("Что делать:")
        logger.error("1. Railway → сервис 'bot' → Variables")
        logger.error("2. Добавьте переменную BOT_TOKEN")
        logger.error("3. Значение: ваш токен от @BotFather")
        logger.error("=" * 60)
        raise ValueError("BOT_TOKEN is required but not set")
    
    # Инициализация базы данных
    logger.info("Инициализация базы данных...")
    try:
        await init_db()
        logger.info("✅ База данных готова")
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации БД: {e}")
        raise
    
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
    try:
        me = await bot.get_me()
        logger.info(f"✅ Бот запущен: @{me.username}")
        logger.info(f"   ID: {me.id}")
        logger.info(f"   Имя: {me.first_name}")
    except Exception as e:
        logger.error("=" * 60)
        logger.error("❌ ОШИБКА ПОДКЛЮЧЕНИЯ К TELEGRAM")
        logger.error("=" * 60)
        logger.error(f"Ошибка: {e}")
        logger.error("")
        logger.error("Возможные причины:")
        logger.error("1. Неверный BOT_TOKEN в переменных окружения Railway")
        logger.error("2. Бот удален или деактивирован в @BotFather")
        logger.error("")
        logger.error("Что делать:")
        logger.error("- Проверьте BOT_TOKEN в Railway → Settings → Variables")
        logger.error("- Проверьте токен в @BotFather (/token)")
        logger.error("=" * 60)
        await bot.session.close()
        raise
    
    logger.info("=" * 60)
    logger.info("🚀 Бот готов к работе!")
    logger.info("   Бот работает 24/7 на Railway")
    logger.info("=" * 60)
    
    # Удаляем webhook и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Запускаем polling (блокирующий вызов - бот будет работать постоянно)
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"❌ Ошибка при polling: {e}", exc_info=True)
        raise
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n" + "=" * 60)
        logger.info("⛔ Получен сигнал остановки")
        logger.info("=" * 60)
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}", exc_info=True)
        raise

