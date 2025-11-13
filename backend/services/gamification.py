"""
Сервис геймификации: начисление баллов и проверка достижений
"""

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from backend.database.models import (
    User, UserProgress, UserCourse, UserAchievement, 
    Achievement, Course, Lesson
)

# Импортируем уведомления (циклический импорт, поэтому внутри функции)


# ========================================
# Константы начисления баллов
# ========================================
POINTS_PER_LESSON = 10  # Баллы за завершение урока
POINTS_PER_COURSE = 100  # Баллы за завершение курса


async def add_points_to_user(
    session: AsyncSession,
    user_id: int,
    points: int,
    reason: str = ""
) -> int:
    """
    Начислить баллы пользователю
    
    Args:
        session: SQLAlchemy сессия
        user_id: ID пользователя
        points: Количество баллов для начисления
        reason: Причина начисления (для логирования)
    
    Returns:
        Новое количество баллов пользователя
    """
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise ValueError(f"User with id {user_id} not found")
    
    user.points += points
    await session.commit()
    await session.refresh(user)
    
    print(f"✅ [Gamification] Начислено {points} баллов пользователю {user.full_name} (ID: {user_id}). Причина: {reason}. Всего баллов: {user.points}")
    
    return user.points


async def award_points_for_lesson_completion(
    session: AsyncSession,
    user_id: int,
    lesson_id: int
) -> int:
    """
    Начислить баллы за завершение урока
    
    Args:
        session: SQLAlchemy сессия
        user_id: ID пользователя
        lesson_id: ID урока
    
    Returns:
        Количество начисленных баллов
    """
    # Проверяем, что урок действительно завершен
    result = await session.execute(
        select(UserProgress).where(
            UserProgress.user_id == user_id,
            UserProgress.lesson_id == lesson_id,
            UserProgress.completed == True
        )
    )
    progress = result.scalar_one_or_none()
    
    if not progress:
        print(f"⚠️ [Gamification] Урок {lesson_id} не завершен пользователем {user_id}")
        return 0
    
    # Начисляем баллы
    new_points = await add_points_to_user(
        session,
        user_id,
        POINTS_PER_LESSON,
        f"Завершение урока {lesson_id}"
    )
    
    return POINTS_PER_LESSON


async def award_points_for_course_completion(
    session: AsyncSession,
    user_id: int,
    course_id: int
) -> int:
    """
    Начислить баллы за завершение курса
    
    Args:
        session: SQLAlchemy сессия
        user_id: ID пользователя
        course_id: ID курса
    
    Returns:
        Количество начисленных баллов
    """
    # Проверяем, что курс действительно завершен
    result = await session.execute(
        select(UserCourse).where(
            UserCourse.user_id == user_id,
            UserCourse.course_id == course_id,
            UserCourse.is_completed == True
        )
    )
    user_course = result.scalar_one_or_none()
    
    if not user_course:
        print(f"⚠️ [Gamification] Курс {course_id} не завершен пользователем {user_id}")
        return 0
    
    # Начисляем баллы
    new_points = await add_points_to_user(
        session,
        user_id,
        POINTS_PER_COURSE,
        f"Завершение курса {course_id}"
    )
    
    return POINTS_PER_COURSE


async def check_and_award_achievements(
    session: AsyncSession,
    user_id: int
) -> list[dict]:
    """
    Проверить условия достижений и начислить их пользователю
    
    Args:
        session: SQLAlchemy сессия
        user_id: ID пользователя
    
    Returns:
        Список новых достижений (словари с id, title, points)
    """
    # Получаем пользователя
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise ValueError(f"User with id {user_id} not found")
    
    # Получаем все достижения
    result = await session.execute(select(Achievement))
    all_achievements = result.scalars().all()
    
    # Получаем уже полученные достижения пользователя
    result = await session.execute(
        select(UserAchievement.achievement_id).where(
            UserAchievement.user_id == user_id
        )
    )
    earned_achievement_ids = {row[0] for row in result.fetchall()}
    
    new_achievements = []
    
    for achievement in all_achievements:
        # Пропускаем уже полученные достижения
        if achievement.id in earned_achievement_ids:
            continue
        
        # Проверяем условие достижения
        if await _check_achievement_condition(session, user_id, achievement):
            # Создаем запись о получении достижения
            user_achievement = UserAchievement(
                user_id=user_id,
                achievement_id=achievement.id,
                earned_at=datetime.now()
            )
            session.add(user_achievement)
            
            # Начисляем баллы за достижение
            if achievement.points > 0:
                await add_points_to_user(
                    session,
                    user_id,
                    achievement.points,
                    f"Достижение: {achievement.title}"
                )
            
            new_achievements.append({
                "id": achievement.id,
                "title": achievement.title,
                "description": achievement.description,
                "points": achievement.points,
                "icon_url": achievement.icon_url
            })
            
            print(f"🏆 [Gamification] Пользователь {user.full_name} получил достижение: {achievement.title}")
            
            # Отправляем уведомление о получении достижения
            try:
                from backend.services.notifications import send_achievement_notification
                await send_achievement_notification(
                    user.telegram_id,
                    achievement.title,
                    achievement.description,
                    achievement.points
                )
            except Exception as e:
                print(f"⚠️ [Gamification] Ошибка отправки уведомления о достижении: {e}")
    
    if new_achievements:
        await session.commit()
    
    return new_achievements


async def _check_achievement_condition(
    session: AsyncSession,
    user_id: int,
    achievement: Achievement
) -> bool:
    """
    Проверить условие достижения
    
    Args:
        session: SQLAlchemy сессия
        user_id: ID пользователя
        achievement: Объект достижения
    
    Returns:
        True если условие выполнено
    """
    condition_type = achievement.condition_type
    condition_value = achievement.condition_value
    
    if condition_type == "courses_completed":
        # Проверяем количество завершенных курсов
        result = await session.execute(
            select(func.count(UserCourse.id)).where(
                UserCourse.user_id == user_id,
                UserCourse.is_completed == True
            )
        )
        completed_count = result.scalar() or 0
        return completed_count >= condition_value
    
    elif condition_type == "category_courses_completed":
        # Проверяем количество завершенных курсов в категории
        # Для этого нужно знать категорию из description или добавить поле category в Achievement
        # Пока упрощенная версия - проверяем все курсы
        result = await session.execute(
            select(func.count(UserCourse.id)).where(
                UserCourse.user_id == user_id,
                UserCourse.is_completed == True
            )
        )
        completed_count = result.scalar() or 0
        return completed_count >= condition_value
    
    elif condition_type == "lessons_completed":
        # Проверяем количество завершенных уроков
        result = await session.execute(
            select(func.count(UserProgress.id)).where(
                UserProgress.user_id == user_id,
                UserProgress.completed == True
            )
        )
        completed_count = result.scalar() or 0
        return completed_count >= condition_value
    
    elif condition_type == "points_earned":
        # Проверяем количество заработанных баллов
        result = await session.execute(
            select(User.points).where(User.id == user_id)
        )
        user_points = result.scalar() or 0
        return user_points >= condition_value
    
    else:
        print(f"⚠️ [Gamification] Неизвестный тип условия: {condition_type}")
        return False


async def check_course_completion(
    session: AsyncSession,
    user_id: int,
    course_id: int
) -> bool:
    """
    Проверить, завершен ли курс пользователем (все уроки пройдены)
    Если да - обновить UserCourse.is_completed и начислить баллы
    
    Args:
        session: SQLAlchemy сессия
        user_id: ID пользователя
        course_id: ID курса
    
    Returns:
        True если курс только что был завершен
    """
    # Получаем UserCourse
    result = await session.execute(
        select(UserCourse).where(
            UserCourse.user_id == user_id,
            UserCourse.course_id == course_id
        )
    )
    user_course = result.scalar_one_or_none()
    
    if not user_course:
        return False
    
    # Если уже помечен как завершенный - ничего не делаем
    if user_course.is_completed:
        return False
    
    # Получаем все уроки курса
    result = await session.execute(
        select(Lesson.id).where(Lesson.course_id == course_id)
    )
    all_lesson_ids = [row[0] for row in result.fetchall()]
    
    if not all_lesson_ids:
        return False
    
    # Проверяем, все ли уроки завершены
    result = await session.execute(
        select(func.count(UserProgress.id)).where(
            UserProgress.user_id == user_id,
            UserProgress.lesson_id.in_(all_lesson_ids),
            UserProgress.completed == True
        )
    )
    completed_lessons_count = result.scalar() or 0
    
    # Если все уроки завершены
    if completed_lessons_count >= len(all_lesson_ids):
        user_course.is_completed = True
        user_course.completed_at = datetime.now()
        await session.commit()
        
        # Начисляем баллы за завершение курса
        await award_points_for_course_completion(session, user_id, course_id)
        
        # Проверяем достижения
        await check_and_award_achievements(session, user_id)
        
        print(f"🎉 [Gamification] Пользователь {user_id} завершил курс {course_id}")
        return True
    
    return False

