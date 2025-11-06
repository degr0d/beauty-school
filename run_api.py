"""
Запуск только FastAPI сервера
Для разработки и тестирования API
"""

import asyncio
import uvicorn
from backend.webapp.app import create_app
from backend.database.database import init_db

async def setup_database():
    """
    Инициализирует БД (создает таблицы если их нет)
    В продакшене миграции должны выполняться через alembic
    """
    try:
        print("🔧 Инициализация базы данных...")
        
        # Пытаемся выполнить миграции перед инициализацией
        try:
            import subprocess
            import sys
            print("🔄 Выполнение миграций Alembic...")
            result = subprocess.run(
                [sys.executable, "-m", "alembic", "upgrade", "head"],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                print("✅ Миграции применены успешно")
            else:
                print(f"⚠️ Миграции не выполнены: {result.stderr}")
                print("💡 Продолжаем с инициализацией БД...")
        except Exception as migration_error:
            print(f"⚠️ Ошибка при выполнении миграций: {migration_error}")
            print("💡 Продолжаем с инициализацией БД...")
        
        await init_db()
        print("✅ База данных готова")
    except Exception as e:
        print(f"⚠️ Ошибка инициализации БД: {e}")
        print("💡 Если это первое развертывание - выполните: alembic upgrade head")

if __name__ == "__main__":
    """
    Запуск FastAPI сервера на порту 8000
    Swagger UI: http://localhost:8000/api/docs
    ReDoc: http://localhost:8000/api/redoc
    Health: http://localhost:8000/health
    """
    
    # Инициализируем БД перед запуском (fallback если миграции не выполнены)
    asyncio.run(setup_database())
    
    app = create_app()
    
    print("=" * 60)
    print("Beauty School API Server")
    print("=" * 60)
    print()
    print("Swagger UI:  http://localhost:8000/api/docs")
    print("ReDoc:       http://localhost:8000/api/redoc")
    print("Health:      http://localhost:8000/health")
    print()
    print("=" * 60)
    
    # Railway использует переменную PORT, если она установлена
    import os
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

