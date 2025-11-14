#!/usr/bin/env python3
"""
Скрипт для отправки запланированных уведомлений
Запускается по расписанию (например, через cron: раз в день)

Использование:
    python scripts/send_scheduled_notifications.py
"""

import asyncio
import sys
import os

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.scheduled_notifications import run_scheduled_notifications


if __name__ == "__main__":
    print("🚀 Запуск отправки запланированных уведомлений...")
    asyncio.run(run_scheduled_notifications())
    print("✅ Готово!")


