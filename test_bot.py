#!/usr/bin/env python3
"""
Быстрый тест запуска бота для диагностики проблем
"""

import asyncio
import sys
import logging
from dotenv import load_dotenv

# Загружаем .env
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_all():
    """Тестирует все компоненты по порядку"""
    
    print("\n" + "="*60)
    print("🔍 ДИАГНОСТИКА БОТА")
    print("="*60 + "\n")
    
    # 1. Проверка конфигурации
    print("[1/4] Проверка конфигурации...")
    try:
        from backend.config import settings
        if not settings.BOT_TOKEN or settings.BOT_TOKEN.startswith("123456"):
            print("❌ BOT_TOKEN не настроен в .env файле!")
            return False
        print(f"✅ BOT_TOKEN настроен: {settings.BOT_TOKEN[:10]}...")
    except Exception as e:
        print(f"❌ Ошибка загрузки конфигурации: {e}")
        return False
    
    # 2. Проверка базы данных
    print("\n[2/4] Проверка подключения к базе данных...")
    try:
        from backend.database.database import init_db
        await init_db()
        print("✅ База данных подключена")
    except Exception as e:
        print(f"❌ Ошибка БД: {e}")
        print("   Проверьте:")
        print("   - Docker контейнеры запущены: docker-compose ps")
        print("   - Параметры БД в .env файле")
        return False
    
    # 3. Проверка бота
    print("\n[3/4] Проверка Telegram бота...")
    try:
        from aiogram import Bot
        bot = Bot(token=settings.BOT_TOKEN)
        me = await bot.get_me()
        await bot.session.close()
        print(f"✅ Бот подключен: @{me.username} (ID: {me.id})")
    except Exception as e:
        print(f"❌ Ошибка подключения к Telegram: {e}")
        print("   Возможные причины:")
        print("   - Неверный BOT_TOKEN")
        print("   - Нет интернета")
        print("   - VPN не включен (Telegram API заблокирован)")
        return False
    
    # 4. Проверка обработчиков
    print("\n[4/4] Проверка обработчиков бота...")
    try:
        from backend.bot.bot import setup_bot_handlers
        from aiogram import Dispatcher
        from aiogram.fsm.storage.memory import MemoryStorage
        
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)
        setup_bot_handlers(dp)
        print("✅ Обработчики зарегистрированы")
    except Exception as e:
        print(f"❌ Ошибка регистрации обработчиков: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "="*60)
    print("✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ!")
    print("="*60)
    print("\nБот готов к запуску. Используйте:")
    print("  - F5 в VS Code: выберите '🚀 Backend (Bot + API)'")
    print("  - Или: python run_all.py")
    print("  - Или: ./launch.sh\n")
    
    return True

if __name__ == "__main__":
    try:
        result = asyncio.run(test_all())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Прервано пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

