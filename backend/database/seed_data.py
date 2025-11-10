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
            "category": "Маникюр и педикюр",
            "is_top": True,
            "price": 0,
            "duration_hours": 10,
            "cover_image_url": "https://via.placeholder.com/400x200?text=Manicure+Course",
            "lessons": [
                {"title": "Введение в маникюр", "order": 1, "description": "Основы маникюра и инструменты", "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "video_duration": 600, "is_free": True},
                {"title": "Подготовка ногтей", "order": 2, "description": "Правильная подготовка ногтевой пластины", "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "video_duration": 900},
                {"title": "Техника нанесения гель-лака", "order": 3, "description": "Пошаговая техника нанесения", "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "video_duration": 1200},
                {"title": "Простой дизайн", "order": 4, "description": "Базовые техники дизайна", "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "video_duration": 1800},
                {"title": "Снятие покрытия", "order": 5, "description": "Безопасное снятие гель-лака", "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "video_duration": 600},
            ]
        },
        {
            "title": "Наращивание ресниц: классика",
            "description": "Освой технику классического наращивания ресниц",
            "full_description": "Полный курс по классическому наращиванию ресниц. Изучи теорию, практику и секреты профессионалов.",
            "category": "Ресницы и брови",
            "is_top": True,
            "price": 0,
            "duration_hours": 15,
            "cover_image_url": "https://via.placeholder.com/400x200?text=Eyelashes+Course",
            "lessons": [
                {"title": "Теория наращивания", "order": 1, "description": "Основы классического наращивания", "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "video_duration": 900, "is_free": True},
                {"title": "Материалы и инструменты", "order": 2, "description": "Выбор материалов для работы", "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "video_duration": 1200},
                {"title": "Техника поресничного наращивания", "order": 3, "description": "Практика наращивания", "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "video_duration": 2400},
                {"title": "Коррекция и снятие", "order": 4, "description": "Техника коррекции и безопасного снятия", "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "video_duration": 1500},
            ]
        },
        {
            "title": "Маркетинг для мастеров",
            "description": "Продвигай свои услуги в Instagram и TikTok",
            "full_description": "Научись продвигать свои услуги в соцсетях, привлекать клиентов и повышать средний чек.",
            "category": "Своё дело",
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
            "category": "Маникюр и педикюр",
            "is_top": False,
            "price": 0,
            "duration_hours": 12,
            "cover_image_url": "https://via.placeholder.com/400x200?text=Pedicure+Course",
            "lessons": [
                {"title": "Анатомия стопы", "order": 1, "description": "Строение стопы и ногтей", "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "video_duration": 900, "is_free": True},
                {"title": "Медицинский педикюр", "order": 2, "description": "Техника медицинского педикюра", "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "video_duration": 2100},
                {"title": "Аппаратный педикюр", "order": 3, "description": "Работа с аппаратом", "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "video_duration": 2400},
            ]
        },
        {
            "title": "Своё дело: с чего начать",
            "description": "Открой свой салон или студию",
            "full_description": "Гайд по открытию своего дела: от бизнес-плана до первых клиентов.",
            "category": "Своё дело",
            "is_top": False,
            "price": 0,
            "duration_hours": 6,
            "cover_image_url": "https://via.placeholder.com/400x200?text=Business+Course",
            "lessons": [
                {"title": "Бизнес-план", "order": 1, "description": "Составление бизнес-плана для салона", "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "video_duration": 1800, "is_free": True},
                {"title": "Регистрация ИП", "order": 2, "description": "Пошаговая регистрация ИП", "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "video_duration": 1200},
                {"title": "Первые клиенты", "order": 3, "description": "Как найти первых клиентов", "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "video_duration": 1500},
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
                print(f"⏭️  Пропущен: Курс '{course_data['title']}' уже существует")
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
            
            print(f"✅ Создан курс: {course.title} ({len(lessons_data)} уроков)")
        
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
                print(f"⏭️  Пропущено: Достижение '{ach_data['title']}' уже существует")
                continue
            
            achievement = Achievement(**ach_data)
            session.add(achievement)
            print(f"✅ Создано достижение: {achievement.title}")
        
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
            "category": "Ресницы и брови",
            "telegram_link": "https://t.me/+example_eyelashes"
        },
        {
            "title": "Маникюр и педикюр",
            "description": "Делимся опытом и советами по маникюру и педикюру. Новые техники и тренды.",
            "type": "profession",
            "city": None,
            "category": "Маникюр и педикюр",
            "telegram_link": "https://t.me/+example_manicure"
        },
        {
            "title": "Маркетинг для мастеров",
            "description": "Учимся продвигать свои услуги в соцсетях и привлекать клиентов.",
            "type": "profession",
            "city": None,
            "category": "Своё дело",
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
                print(f"⏭️  Пропущено: Сообщество '{comm_data['title']}' уже существует")
                continue
            
            community = Community(**comm_data)
            session.add(community)
            print(f"✅ Создано сообщество: {community.title}")
        
        await session.commit()


async def main():
    """Главная функция"""
    print("🌱 Начинаем заполнение БД тестовыми данными...")
    print("=" * 60)
    print()
    
    print("📚 Создание курсов...")
    await seed_courses()
    print()
    
    print("🏆 Создание достижений...")
    await seed_achievements()
    print()
    
    print("👥 Создание сообществ...")
    await seed_communities()
    print()
    
    print("=" * 60)
    print("✅ Готово! База данных заполнена тестовыми данными.")


if __name__ == "__main__":
    asyncio.run(main())


# ========================================
# Запуск:
# ========================================
# python -m backend.database.seed_data

