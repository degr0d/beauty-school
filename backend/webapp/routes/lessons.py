"""
API эндпоинты для уроков
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from backend.database import get_session, Lesson, UserProgress, User, UserCourse, Course, Certificate
from backend.webapp.schemas import LessonDetailResponse
from backend.webapp.middleware import get_telegram_user
from backend.config import settings
from backend.services.gamification import (
    award_points_for_lesson_completion,
    check_course_completion
)
from backend.services.certificates import (
    generate_certificate_number,
    save_certificate_to_storage,
    get_certificate_url
)

router = APIRouter()


@router.get("/{lesson_id}", response_model=LessonDetailResponse)
async def get_lesson(
    lesson_id: int,
    user: dict = Depends(get_telegram_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Получить детали урока (видео, PDF и т.д.)
    Доступ только если курс оплачен (или урок бесплатный)
    """
    telegram_id = user["id"]
    
    # АДМИНЫ ВСЕГДА ИМЕЮТ ДОСТУП К ЛЮБЫМ УРОКАМ
    is_admin = telegram_id in settings.admin_ids_list
    
    # Получаем пользователя
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    db_user = result.scalar_one_or_none()
    
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Получаем урок
    result = await session.execute(
        select(Lesson).where(Lesson.id == lesson_id)
    )
    lesson = result.scalar_one_or_none()
    
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    # Если урок бесплатный или пользователь админ - разрешаем доступ
    if lesson.is_free or is_admin:
        return LessonDetailResponse(
            id=lesson.id,
            course_id=lesson.course_id,
            title=lesson.title,
            description=lesson.description,
            order=lesson.order,
            video_url=lesson.video_url,
            video_duration=lesson.video_duration,
            pdf_url=lesson.pdf_url,
            is_free=lesson.is_free
        )
    
    # Для платных уроков проверяем доступ к курсу
    result = await session.execute(
        select(UserCourse).where(
            UserCourse.user_id == db_user.id,
            UserCourse.course_id == lesson.course_id
        )
    )
    user_course = result.scalar_one_or_none()
    
    if not user_course:
        raise HTTPException(
            status_code=403,
            detail="Access denied. You need to purchase this course to access lessons."
        )
    
    return LessonDetailResponse(
        id=lesson.id,
        course_id=lesson.course_id,
        title=lesson.title,
        description=lesson.description,
        order=lesson.order,
        video_url=lesson.video_url,
        video_duration=lesson.video_duration,
        pdf_url=lesson.pdf_url,
        is_free=lesson.is_free
    )


@router.post("/{lesson_id}/complete")
async def complete_lesson(
    lesson_id: int,
    user: dict = Depends(get_telegram_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Отметить урок как пройденный
    Доступ только если курс оплачен
    """
    telegram_id = user["id"]
    
    # АДМИНЫ ВСЕГДА МОГУТ ЗАВЕРШАТЬ УРОКИ
    is_admin = telegram_id in settings.admin_ids_list
    
    # Получаем пользователя
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    db_user = result.scalar_one_or_none()
    
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Проверяем, существует ли урок
    result = await session.execute(
        select(Lesson).where(Lesson.id == lesson_id)
    )
    lesson = result.scalar_one_or_none()
    
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    # Проверяем доступ к курсу (если урок платный и не админ)
    if not lesson.is_free and not is_admin:
        result = await session.execute(
            select(UserCourse).where(
                UserCourse.user_id == db_user.id,
                UserCourse.course_id == lesson.course_id
            )
        )
        user_course = result.scalar_one_or_none()
        
        if not user_course:
            raise HTTPException(
                status_code=403,
                detail="Access denied. You need to purchase this course to complete lessons."
            )
    
    # Проверяем, есть ли уже запись о прогрессе
    result = await session.execute(
        select(UserProgress).where(
            UserProgress.user_id == db_user.id,
            UserProgress.lesson_id == lesson_id
        )
    )
    progress = result.scalar_one_or_none()
    
    if progress:
        # Обновляем существующую запись
        progress.completed = True
        progress.completed_at = datetime.now()
    else:
        # Создаём новую запись
        progress = UserProgress(
            user_id=db_user.id,
            lesson_id=lesson_id,
            completed=True,
            completed_at=datetime.now()
        )
        session.add(progress)
    
    await session.commit()
    
    # Начисляем баллы за завершение урока
    try:
        await award_points_for_lesson_completion(session, db_user.id, lesson_id)
        print(f"✅ [Lessons] Начислены баллы за урок {lesson_id} пользователю {db_user.full_name}")
    except Exception as e:
        print(f"⚠️ [Lessons] Ошибка начисления баллов за урок: {e}")
    
    # Проверяем, завершен ли курс (все уроки пройдены)
    # Это автоматически начислит баллы за курс и проверит достижения
    course_completed = False
    try:
        course_completed = await check_course_completion(session, db_user.id, lesson.course_id)
        if course_completed:
            print(f"🎉 [Lessons] Курс {lesson.course_id} завершен пользователем {db_user.full_name}")
    except Exception as e:
        print(f"⚠️ [Lessons] Ошибка проверки завершения курса: {e}")
    
    # Если курс завершен - генерируем сертификат
    if course_completed:
        try:
            # Проверяем, нет ли уже сертификата
            result = await session.execute(
                select(Certificate).where(
                    Certificate.user_id == db_user.id,
                    Certificate.course_id == lesson.course_id
                )
            )
            existing_cert = result.scalar_one_or_none()
            
            if not existing_cert:
                # Получаем курс
                result = await session.execute(
                    select(Course).where(Course.id == lesson.course_id)
                )
                course = result.scalar_one_or_none()
                
                if course:
                    # Генерируем сертификат
                    cert_number = generate_certificate_number(db_user.id, course.id)
                    filepath = save_certificate_to_storage(db_user, course, cert_number)
                    cert_url = get_certificate_url(filepath)
                    
                    # Создаем запись в БД
                    certificate = Certificate(
                        user_id=db_user.id,
                        course_id=course.id,
                        certificate_number=cert_number,
                        certificate_url=cert_url,
                        issued_at=datetime.now()
                    )
                    session.add(certificate)
                    await session.commit()
                    
                    print(f"🏆 [Lessons] Сертификат создан для пользователя {db_user.full_name}, курс: {course.title}")
            else:
                print(f"ℹ️ [Lessons] Сертификат для курса {lesson.course_id} уже существует")
        except Exception as e:
            print(f"⚠️ [Lessons] Ошибка генерации сертификата: {e}")
    
    return {
        "status": "success", 
        "message": "Lesson marked as completed",
        "course_completed": course_completed
    }


# ========================================
# Пример запроса:
# ========================================
# GET /api/lessons/1
# POST /api/lessons/1/complete

