"""Быстрая проверка курсов в БД"""
import asyncio
from sqlalchemy import select
from backend.database.database import async_session
from backend.database.models import Course

async def check():
    async with async_session() as session:
        result = await session.execute(select(Course))
        courses = result.scalars().all()
        
        print(f"\nKursov v BD: {len(courses)}")
        
        if courses:
            print("\nSpisok kursov:")
            for course in courses:
                print(f"  - {course.title} ({course.category})")
        else:
            print("\nKURSOV NET! Zapusti: python backend/database/seed_data.py")

if __name__ == "__main__":
    asyncio.run(check())

