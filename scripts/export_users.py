"""
Экспорт пользователей из локальной БД в Railway БД

Использование:
    python3 scripts/export_users.py
"""

import asyncio
import os
import sys
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.models import User
from backend.config import settings


async def get_local_users():
    """Получить всех пользователей из локальной БД"""
    print("🔍 Подключение к локальной БД...")
    
    # Используем локальную БД из .env
    local_db_url = settings.database_url
    
    engine = create_async_engine(local_db_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        
        print(f"✅ Найдено пользователей в локальной БД: {len(users)}")
        for user in users:
            print(f"   - {user.full_name} (Telegram ID: {user.telegram_id})")
        
        await engine.dispose()
        return users


async def import_users_to_railway(users):
    """Импортировать пользователей в Railway БД"""
    railway_db_url = os.getenv("RAILWAY_DATABASE_URL")
    
    if not railway_db_url:
        print("\n❌ Ошибка: RAILWAY_DATABASE_URL не установлен!")
        print("\n💡 Как получить DATABASE_URL из Railway:")
        print("   1. Зайдите на railway.app")
        print("   2. Ваш проект → PostgreSQL сервис → Variables")
        print("   3. Скопируйте DATABASE_URL")
        print("   4. Установите: export RAILWAY_DATABASE_URL='postgresql://...'")
        print("   5. Или передайте как аргумент: python3 scripts/export_users.py 'postgresql://...'")
        return False
    
    # Конвертируем postgresql:// в postgresql+asyncpg://
    if railway_db_url.startswith("postgresql://"):
        railway_db_url = railway_db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    print(f"\n🔍 Подключение к Railway БД...")
    print(f"   URL: {railway_db_url[:50]}...")
    
    engine = create_async_engine(railway_db_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    imported_count = 0
    skipped_count = 0
    
    async with async_session() as session:
        for user in users:
            # Проверяем, существует ли пользователь уже
            result = await session.execute(
                select(User).where(User.telegram_id == user.telegram_id)
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print(f"⏭️  Пропущен (уже существует): {user.full_name} (ID: {user.telegram_id})")
                skipped_count += 1
                continue
            
            # Создаем нового пользователя
            new_user = User(
                telegram_id=user.telegram_id,
                username=user.username,
                full_name=user.full_name,
                phone=user.phone,
                city=user.city,
                points=user.points,
                consent_personal_data=user.consent_personal_data,
                created_at=user.created_at,
            )
            session.add(new_user)
            imported_count += 1
            print(f"✅ Импортирован: {user.full_name} (ID: {user.telegram_id})")
        
        await session.commit()
        await engine.dispose()
    
    print(f"\n📊 Итоги:")
    print(f"   ✅ Импортировано: {imported_count}")
    print(f"   ⏭️  Пропущено (уже есть): {skipped_count}")
    print(f"   📦 Всего обработано: {len(users)}")
    
    return True


async def main():
    print("=" * 60)
    print("🚀 Экспорт пользователей из локальной БД в Railway")
    print("=" * 60)
    print()
    
    # Проверяем аргументы командной строки
    if len(sys.argv) > 1:
        railway_url = sys.argv[1]
        os.environ["RAILWAY_DATABASE_URL"] = railway_url
    
    # Получаем пользователей из локальной БД
    users = await get_local_users()
    
    if not users:
        print("\n⚠️  Пользователей в локальной БД не найдено")
        return
    
    # Импортируем в Railway
    print("\n" + "=" * 60)
    success = await import_users_to_railway(users)
    
    if success:
        print("\n✅ Экспорт завершен!")
        print("\n💡 Теперь проверьте профиль в Mini App")
    else:
        print("\n❌ Экспорт не завершен. Проверьте ошибки выше.")


if __name__ == "__main__":
    asyncio.run(main())

