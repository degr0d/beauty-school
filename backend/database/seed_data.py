"""
Скрипт для заполнения БД тестовыми данными
Запуск: python -m backend.database.seed_data
"""

import asyncio
from sqlalchemy import select

from backend.database import async_session
from backend.database.models import Course, Lesson, Achievement, Community


async def seed_courses():
    """Создаёт тестовые курсы"""
    
    courses_data = [
        {
            "title": "Основы маникюра для начинающих",
            "description": "Научись делать идеальный маникюр с нуля",
            "full_description": "Этот курс подойдёт для тех, кто хочет освоить маникюр с нуля. Ты узнаешь о правильной подготовке ногтей, технике нанесения покрытия и дизайне.",
            "category": "manicure",
            "is_top": True,
            "price": 0,
            "duration_hours": 10,
            "cover_image_url": "https://via.placeholder.com/400x200?text=Manicure+Course",
            "lessons": [
                {"title": "Введение в маникюр", "order": 1, "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "is_free": True},
                {"title": "Подготовка ногтей", "order": 2, "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
                {"title": "Техника нанесения гель-лака", "order": 3, "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
                {"title": "Простой дизайн", "order": 4, "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
                {"title": "Снятие покрытия", "order": 5, "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
            ]
        },
        {
            "title": "Наращивание ресниц: классика",
            "description": "Освой технику классического наращивания ресниц",
            "full_description": "Полный курс по классическому наращиванию ресниц. Изучи теорию, практику и секреты профессионалов.",
            "category": "eyelashes",
            "is_top": True,
            "price": 0,
            "duration_hours": 15,
            "cover_image_url": "https://via.placeholder.com/400x200?text=Eyelashes+Course",
            "lessons": [
                {"title": "Теория наращивания", "order": 1, "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "is_free": True},
                {"title": "Материалы и инструменты", "order": 2, "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
                {"title": "Техника поресничного наращивания", "order": 3, "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
                {"title": "Коррекция и снятие", "order": 4, "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
            ]
        },
        {
            "title": "Маркетинг для мастеров",
            "description": "Продвигай свои услуги в Instagram и TikTok",
            "full_description": "Научись продвигать свои услуги в соцсетях, привлекать клиентов и повышать средний чек.",
            "category": "marketing",
            "is_top": False,
            "price": 0,
            "duration_hours": 8,
            "cover_image_url": "https://via.placeholder.com/400x200?text=Marketing+Course",
            "lessons": [
                {"title": "Создание профиля в Instagram", "order": 1, "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "is_free": True},
                {"title": "Контент-план", "order": 2, "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
                {"title": "Работа с отзывами", "order": 3, "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
            ]
        },
        {
            "title": "Педикюр: полный курс",
            "description": "От базового ухода до аппаратного педикюра",
            "full_description": "Комплексный курс по педикюру: медицинский, европейский и аппаратный педикюр.",
            "category": "pedicure",
            "is_top": False,
            "price": 0,
            "duration_hours": 12,
            "cover_image_url": "https://via.placeholder.com/400x200?text=Pedicure+Course",
            "lessons": [
                {"title": "Анатомия стопы", "order": 1, "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "is_free": True},
                {"title": "Медицинский педикюр", "order": 2, "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
                {"title": "Аппаратный педикюр", "order": 3, "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
            ]
        },
        {
            "title": "Своё дело: с чего начать",
            "description": "Открой свой салон или студию",
            "full_description": "Гайд по открытию своего дела: от бизнес-плана до первых клиентов.",
            "category": "business",
            "is_top": False,
            "price": 0,
            "duration_hours": 6,
            "cover_image_url": "https://via.placeholder.com/400x200?text=Business+Course",
            "lessons": [
                {"title": "Бизнес-план", "order": 1, "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "is_free": True},
                {"title": "Регистрация ИП", "order": 2, "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
                {"title": "Первые клиенты", "order": 3, "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
            ]
        },
    ]
    
    async with async_session() as session:
        for course_data in courses_data:
            # Проверяем, существует ли курс
            result = await session.execute(
                select(Course).where(Course.title == course_data["title"])
            )
            existing_course = result.scalar_one_or_none()
            
            if existing_course:
                print(f"Skip: Kurs '{course_data['title']}' uzhe suschestvuet")
                continue
            
            # Извлекаем уроки
            lessons_data = course_data.pop("lessons")
            
            # Создаём курс
            course = Course(**course_data)
            session.add(course)
            await session.flush()  # Получаем ID курса
            
            # Создаём уроки
            for lesson_data in lessons_data:
                lesson = Lesson(
                    course_id=course.id,
                    **lesson_data
                )
                session.add(lesson)
            
            print(f"OK: Sozdan kurs: {course.title} ({len(lessons_data)} urokov)")
        
        await session.commit()


async def seed_achievements():
    """Создаёт тестовые достижения"""
    
    achievements_data = [
        {
            "title": "Первый шаг",
            "description": "Завершён первый курс",
            "points": 100,
            "condition_type": "courses_completed",
            "condition_value": 1,
            "icon_url": "🎓"
        },
        {
            "title": "Мастер ногтей",
            "description": "Завершено 3 курса по маникюру",
            "points": 300,
            "condition_type": "category_courses_completed",
            "condition_value": 3,
            "icon_url": "💅"
        },
        {
            "title": "Специалист по ресницам",
            "description": "Завершено 2 курса по ресницам",
            "points": 200,
            "condition_type": "category_courses_completed",
            "condition_value": 2,
            "icon_url": "👁"
        },
    ]
    
    async with async_session() as session:
        for ach_data in achievements_data:
            # Проверяем существование
            result = await session.execute(
                select(Achievement).where(Achievement.title == ach_data["title"])
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                print(f"Skip: Dostizhenie '{ach_data['title']}' uzhe suschestvuet")
                continue
            
            achievement = Achievement(**ach_data)
            session.add(achievement)
            print(f"OK: Sozdano dostizhenie: {achievement.title}")
        
        await session.commit()


async def seed_communities():
    """Создаёт тестовые сообщества/чаты"""
    
    communities_data = [
        {
            "title": "Мастера Москвы",
            "description": "Чат для мастеров из Москвы. Обмениваемся опытом, советами и находим клиентов.",
            "type": "city",
            "city": "Москва",
            "category": None,
            "telegram_link": "https://t.me/+example_moscow"
        },
        {
            "title": "Мастера Санкт-Петербурга",
            "description": "Сообщество мастеров Санкт-Петербурга",
            "type": "city",
            "city": "Санкт-Петербург",
            "category": None,
            "telegram_link": "https://t.me/+example_spb"
        },
        {
            "title": "Ресницы и брови",
            "description": "Обсуждаем техники наращивания ресниц и коррекции бровей. Делимся секретами профессионалов.",
            "type": "profession",
            "city": None,
            "category": "eyelashes",
            "telegram_link": "https://t.me/+example_eyelashes"
        },
        {
            "title": "Маникюр и педикюр",
            "description": "Делимся опытом и советами по маникюру и педикюру. Новые техники и тренды.",
            "type": "profession",
            "city": None,
            "category": "manicure",
            "telegram_link": "https://t.me/+example_manicure"
        },
        {
            "title": "Маркетинг для мастеров",
            "description": "Учимся продвигать свои услуги в соцсетях и привлекать клиентов.",
            "type": "profession",
            "city": None,
            "category": "marketing",
            "telegram_link": "https://t.me/+example_marketing"
        },
    ]
    
    async with async_session() as session:
        for comm_data in communities_data:
            # Проверяем существование
            result = await session.execute(
                select(Community).where(Community.title == comm_data["title"])
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                print(f"Skip: Soobschestvo '{comm_data['title']}' uzhe suschestvuet")
                continue
            
            community = Community(**comm_data)
            session.add(community)
            print(f"OK: Sozdano soobschestvo: {community.title}")
        
        await session.commit()


async def main():
    """Главная функция"""
    print("Nachinaem zapolnenie BD testovymi dannymi...")
    print()
    
    await seed_courses()
    print()
    await seed_achievements()
    print()
    await seed_communities()
    print()
    
    print("Gotovo! Baza dannyh zapolnena.")


if __name__ == "__main__":
    asyncio.run(main())


# ========================================
# Запуск:
# ========================================
# python -m backend.database.seed_data

