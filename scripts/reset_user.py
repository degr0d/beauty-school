"""
Удалить пользователя(ей) из БД для повторного тестирования

Использование:
    python3 scripts/reset_user.py              # Удалить всех пользователей
    python3 scripts/reset_user.py 123456789     # Удалить конкретного пользователя по telegram_id
"""
import asyncio
import sys
from sqlalchemy import delete, select
from backend.database.database import async_session, init_db
from backend.database.models import User


async def reset_all():
    """Удалить всех пользователей из БД"""
    await init_db()
    
    async with async_session() as session:
        # Сначала показываем всех пользователей
        result = await session.execute(select(User))
        users = result.scalars().all()
        
        if not users:
            print("\n[INFO] Пользователей нет в БД\n")
            return
        
        print(f"\n[INFO] Найдено пользователей: {len(users)}")
        for user in users:
            print(f"  - {user.full_name} (Telegram ID: {user.telegram_id})")
        
        # Удаляем всех
        result = await session.execute(delete(User))
        await session.commit()
        
        print(f"\n[OK] Удалено пользователей: {result.rowcount}")
        print("[OK] Теперь можно зарегистрироваться заново!\n")


async def reset_user(telegram_id: int):
    """Удалить конкретного пользователя по telegram_id"""
    await init_db()
    
    async with async_session() as session:
        # Проверяем, существует ли пользователь
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            print(f"\n[INFO] Пользователь с Telegram ID {telegram_id} не найден в БД\n")
            return
        
        print(f"\n[INFO] Найден пользователь: {user.full_name} (ID: {user.id})")
        
        # Удаляем пользователя
        result = await session.execute(
            delete(User).where(User.telegram_id == telegram_id)
        )
        await session.commit()
        
        if result.rowcount > 0:
            print(f"[OK] Пользователь удален из БД!")
            print(f"[OK] Теперь можно зарегистрироваться заново!\n")
        else:
            print(f"[INFO] Пользователь не найден (может быть уже удален)\n")


async def main():
    if len(sys.argv) > 1:
        # Удалить конкретного пользователя
        try:
            telegram_id = int(sys.argv[1])
            await reset_user(telegram_id)
        except ValueError:
            print(f"[ERROR] Неверный Telegram ID: {sys.argv[1]}")
            print("Использование: python3 scripts/reset_user.py [telegram_id]")
            print("Для удаления всех: python3 scripts/reset_user.py")
    else:
        # Удалить всех пользователей
        print("[WARNING] Вы собираетесь удалить ВСЕХ пользователей из БД!")
        response = input("Продолжить? (yes/no): ")
        if response.lower() in ['yes', 'y', 'да', 'д']:
            await reset_all()
        else:
            print("\n[INFO] Операция отменена\n")


if __name__ == "__main__":
    asyncio.run(main())

