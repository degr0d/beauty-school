"""
Проверка зарегистрированных пользователей в БД
"""

import asyncio
from sqlalchemy import select
from backend.database.database import async_session, init_db
from backend.database.models import User


async def check_users():
    """Показывает всех пользователей из БД"""
    
    print("=" * 60)
    print("Proverka polzovateley v BD")
    print("=" * 60)
    print()
    
    await init_db()
    
    async with async_session() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        
        if not users:
            print("X Polzovateley net v BD")
            print()
            print("Vozmozhno registratsiya eshe ne zavershena.")
            return
        
        print(f"OK! Nayden(o) {len(users)} polzovateley:")
        print()
        
        for user in users:
            print(f"ID: {user.id}")
            print(f"   Telegram ID: {user.telegram_id}")
            print(f"   Username: @{user.username or '(ne ukazano)'}")
            print(f"   FIO: {user.full_name}")
            print(f"   Telefon: {user.phone}")
            print(f"   Data registratsii: {user.created_at}")
            print(f"   Soglasie na dannye: {'Da' if user.consent_personal_data else 'Net'}")
            print("-" * 60)


if __name__ == "__main__":
    asyncio.run(check_users())

