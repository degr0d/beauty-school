"""
API эндпоинты для уроков
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from backend.database import get_session, Lesson, UserProgress, User, UserCourse, Course, Certificate, Community
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
from backend.services.notifications import (
    send_lesson_completed_notification,
    send_course_completed_notification,
    send_next_course_recommendation,
    send_community_recommendation
)
from backend.services.challenges import check_all_user_challenges

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
    
    # Проверяем, является ли это первым уроком курса (order = 1)
    # Первый урок всегда бесплатный для превью
    is_first_lesson = lesson.order == 1
    
    # Если урок бесплатный, первый урок, или пользователь админ - разрешаем доступ
    if lesson.is_free or is_first_lesson or is_admin:
        return LessonDetailResponse(
            id=lesson.id,
            course_id=lesson.course_id,
            title=lesson.title,
            description=lesson.description,
            order=lesson.order,
            video_url=lesson.video_url,
            video_duration=lesson.video_duration,
            pdf_url=lesson.pdf_url,
            is_free=lesson.is_free or is_first_lesson  # Первый урок помечаем как бесплатный
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
    # Первый урок (order=1) всегда доступен для завершения (превью)
    is_first_lesson = lesson.order == 1
    
    if not lesson.is_free and not is_first_lesson and not is_admin:
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
    points_earned = 0
    try:
        points_earned = await award_points_for_lesson_completion(session, db_user.id, lesson_id)
        print(f"✅ [Lessons] Начислены баллы за урок {lesson_id} пользователю {db_user.full_name}")
        
        # Отправляем уведомление о завершении урока
        try:
            result = await session.execute(
                select(Course).where(Course.id == lesson.course_id)
            )
            course = result.scalar_one_or_none()
            if course:
                await send_lesson_completed_notification(
                    db_user.telegram_id,
                    lesson.title,
                    course.title,
                    points_earned
                )
        except Exception as e:
            print(f"⚠️ [Lessons] Ошибка отправки уведомления о завершении урока: {e}")
    except Exception as e:
        print(f"⚠️ [Lessons] Ошибка начисления баллов за урок: {e}")
    
    # Проверяем, завершен ли курс (все уроки пройдены)
    # Это автоматически начислит баллы за курс и проверит достижения
    course_completed = False
    completed_course = None
    try:
        course_completed = await check_course_completion(session, db_user.id, lesson.course_id)
        if course_completed:
            print(f"🎉 [Lessons] Курс {lesson.course_id} завершен пользователем {db_user.full_name}")
            
            # Получаем информацию о завершенном курсе
            result = await session.execute(
                select(Course).where(Course.id == lesson.course_id)
            )
            completed_course = result.scalar_one_or_none()
            
            if completed_course:
                # Отправляем уведомление о завершении курса
                try:
                    # Баллы за курс = 100 (из константы POINTS_PER_COURSE)
                    await send_course_completed_notification(
                        db_user.telegram_id,
                        completed_course.title,
                        100  # POINTS_PER_COURSE
                    )
                except Exception as e:
                    print(f"⚠️ [Lessons] Ошибка отправки уведомления о завершении курса: {e}")
                
                # Рекомендуем следующий курс
                try:
                    # Ищем следующий курс (по той же категории или просто другой активный курс)
                    # Сначала ищем по категории
                    result = await session.execute(
                        select(Course)
                        .where(
                            Course.id != completed_course.id,
                            Course.is_active == True,
                            Course.category == completed_course.category
                        )
                        .where(
                            ~select(UserCourse.id).where(
                                UserCourse.user_id == db_user.id,
                                UserCourse.course_id == Course.id
                            ).exists()
                        )
                        .limit(1)
                    )
                    recommended_course = result.scalar_one_or_none()
                    
                    # Если не нашли по категории - ищем любой другой активный курс
                    if not recommended_course:
                        result = await session.execute(
                            select(Course)
                            .where(
                                Course.id != completed_course.id,
                                Course.is_active == True
                            )
                            .where(
                                ~select(UserCourse.id).where(
                                    UserCourse.user_id == db_user.id,
                                    UserCourse.course_id == Course.id
                                ).exists()
                            )
                            .limit(1)
                        )
                        recommended_course = result.scalar_one_or_none()
                    
                    if recommended_course:
                        await send_next_course_recommendation(
                            db_user.telegram_id,
                            recommended_course.title,
                            recommended_course.id
                        )
                        print(f"📚 [Lessons] Рекомендован следующий курс: {recommended_course.title}")
                except Exception as e:
                    print(f"⚠️ [Lessons] Ошибка рекомендации следующего курса: {e}")
                
                # Рекомендуем сообщество (чат)
                try:
                    # Ищем сообщество по категории курса
                    result = await session.execute(
                        select(Community)
                        .where(
                            Community.category == completed_course.category,
                            Community.type == 'profession'
                        )
                        .limit(1)
                    )
                    community = result.scalar_one_or_none()
                    
                    # Если не нашли по категории - ищем по городу пользователя
                    if not community and db_user.city:
                        result = await session.execute(
                            select(Community)
                            .where(
                                Community.city == db_user.city,
                                Community.type == 'city'
                            )
                            .limit(1)
                        )
                        community = result.scalar_one_or_none()
                    
                    # Если все еще не нашли - берем любое активное сообщество
                    if not community:
                        result = await session.execute(
                            select(Community).limit(1)
                        )
                        community = result.scalar_one_or_none()
                    
                    if community:
                        reason = ""
                        if community.category == completed_course.category:
                            reason = "По вашей специальности"
                        elif community.city == db_user.city:
                            reason = "В вашем городе"
                        
                        await send_community_recommendation(
                            db_user.telegram_id,
                            community.title,
                            community.telegram_link,
                            reason
                        )
                        print(f"💬 [Lessons] Рекомендовано сообщество: {community.title}")
                except Exception as e:
                    print(f"⚠️ [Lessons] Ошибка рекомендации сообщества: {e}")
    except Exception as e:
        print(f"⚠️ [Lessons] Ошибка проверки завершения курса: {e}")
    
    # Проверяем прогресс в челленджах
    try:
        await check_all_user_challenges(session, db_user.id)
    except Exception as e:
        print(f"⚠️ [Lessons] Ошибка проверки челленджей: {e}")
    
    # Если курс завершен - генерируем сертификат
    certificate_data = None
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
                    
                    # Обновляем объект certificate чтобы получить id
                    await session.refresh(certificate)
                    
                    # Формируем данные сертификата для ответа
                    certificate_data = {
                        "id": certificate.id,
                        "course_id": certificate.course_id,
                        "course_title": course.title,
                        "certificate_url": certificate.certificate_url,
                        "certificate_number": certificate.certificate_number,
                        "issued_at": certificate.issued_at.isoformat() if hasattr(certificate.issued_at, 'isoformat') else str(certificate.issued_at)
                    }
                    
                    print(f"🏆 [Lessons] Сертификат создан для пользователя {db_user.full_name}, курс: {course.title}")
            else:
                # Если сертификат уже существует - возвращаем его данные
                result = await session.execute(
                    select(Course).where(Course.id == lesson.course_id)
                )
                course = result.scalar_one_or_none()
                
                if course:
                    certificate_data = {
                        "id": existing_cert.id,
                        "course_id": existing_cert.course_id,
                        "course_title": course.title,
                        "certificate_url": existing_cert.certificate_url,
                        "certificate_number": existing_cert.certificate_number,
                        "issued_at": existing_cert.issued_at.isoformat() if hasattr(existing_cert.issued_at, 'isoformat') else str(existing_cert.issued_at)
                    }
                print(f"ℹ️ [Lessons] Сертификат для курса {lesson.course_id} уже существует")
        except Exception as e:
            import traceback
            print(f"⚠️ [Lessons] Ошибка генерации сертификата: {e}")
            print(f"   Traceback: {traceback.format_exc()}")
    
    return {
        "status": "success", 
        "message": "Lesson marked as completed",
        "course_completed": course_completed,
        "certificate": certificate_data
    }


# ========================================
# Пример запроса:
# ========================================
# GET /api/lessons/1
# POST /api/lessons/1/complete

