"""
Скрипт-обертка для запуска правильного сервиса на Railway
Определяет какой сервис запускать по переменной окружения SERVICE_NAME
"""

import os
import sys

# Получаем имя сервиса из переменной окружения
service_name = os.getenv("RAILWAY_SERVICE_NAME", "").lower()

if "bot" in service_name:
    # Запускаем бота
    print("🤖 Запуск бота...")
    from run_bot_production import main
    import asyncio
    asyncio.run(main())
elif "web" in service_name or "api" in service_name:
    # Запускаем API
    print("🌐 Запуск API...")
    import run_api
    # run_api.py уже запускает сервер при импорте
else:
    # По умолчанию пытаемся определить по START_COMMAND
    start_command = os.getenv("START_COMMAND", "")
    
    if "bot" in start_command.lower():
        print("🤖 Запуск бота (из START_COMMAND)...")
        from run_bot_production import main
        import asyncio
        asyncio.run(main())
    elif "api" in start_command.lower() or "run_api" in start_command.lower():
        print("🌐 Запуск API (из START_COMMAND)...")
        import run_api
    else:
        # Если ничего не подошло - запускаем API по умолчанию
        print("⚠️ Не удалось определить сервис, запускаем API по умолчанию")
        print(f"   RAILWAY_SERVICE_NAME={service_name}")
        print(f"   START_COMMAND={start_command}")
        import run_api

