"""
API эндпоинты для проверки доступа пользователя
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_session, User, UserCourse, Payment
from backend.webapp.middleware import get_telegram_user
from backend.config import settings

router = APIRouter()


@router.get("/check")
async def check_access(
    user: dict = Depends(get_telegram_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Проверяет, есть ли у пользователя доступ к платформе
    Доступ есть только если пользователь оплатил хотя бы один курс
    
    Returns:
    {
        "has_access": bool,
        "purchased_courses_count": int,
        "total_payments": int
    }
    """
    # Явно конвертируем telegram_id в int
    telegram_id = int(user.get("id", 0))
    if telegram_id == 0:
        raise HTTPException(status_code=401, detail="Telegram user ID not found in initData")
    
    # Детальное логирование для диагностики
    print(f"🔍 [Access] Проверка доступа для telegram_id={telegram_id} (type: {type(telegram_id)})")
    print(f"🔍 [Access] ADMIN_IDS из настроек: {settings.ADMIN_IDS}")
    print(f"🔍 [Access] admin_ids_list: {settings.admin_ids_list} (type: {type(settings.admin_ids_list)})")
    
    # Проверяем каждый ID отдельно для диагностики
    for admin_id in settings.admin_ids_list:
        print(f"🔍 [Access] Сравнение: {telegram_id} == {admin_id} (type: {type(admin_id)})? {telegram_id == admin_id}")
    
    is_admin = telegram_id in settings.admin_ids_list
    print(f"🔍 [Access] Итоговый результат: is_admin={is_admin}")
    
    # АДМИНЫ ВСЕГДА ИМЕЮТ ДОСТУП
    if is_admin:
        print(f"👑 [Access] Админ - предоставляем полный доступ")
        return {
            "has_access": True,
            "purchased_courses_count": 999,  # Специальное значение для админов
            "total_payments": 0
        }
    
    # Получаем пользователя по telegram_id (BIGINT в БД)
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    db_user = result.scalar_one_or_none()
    
    if not db_user:
        print(f"❌ [Access] Пользователь не найден: telegram_id={telegram_id}")
        raise HTTPException(status_code=404, detail="User not found")
    
    print(f"✅ [Access] Пользователь найден: {db_user.full_name}")
    
    # Проверяем количество оплаченных курсов
    result = await session.execute(
        select(func.count(UserCourse.id)).where(UserCourse.user_id == db_user.id)
    )
    purchased_courses_count = result.scalar() or 0
    
    # Проверяем количество успешных платежей
    result = await session.execute(
        select(func.count(Payment.id)).where(
            Payment.user_id == db_user.id,
            Payment.status == "succeeded"
        )
    )
    total_payments = result.scalar() or 0
    
    # Доступ есть если есть хотя бы один оплаченный курс
    has_access = purchased_courses_count > 0
    
    return {
        "has_access": has_access,
        "purchased_courses_count": purchased_courses_count,
        "total_payments": total_payments
    }


@router.get("/check-course/{course_id}")
async def check_course_access(
    course_id: int,
    user: dict = Depends(get_telegram_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Проверяет, есть ли у пользователя доступ к конкретному курсу
    
    Returns:
    {
        "has_access": bool,
        "course_id": int,
        "purchased_at": str | null
    }
    """
    # Явно конвертируем telegram_id в int
    telegram_id = int(user.get("id", 0))
    if telegram_id == 0:
        raise HTTPException(status_code=401, detail="Telegram user ID not found in initData")
    
    # АДМИНЫ ВСЕГДА ИМЕЮТ ДОСТУП К ЛЮБОМУ КУРСУ
    if telegram_id in settings.admin_ids_list:
        return {
            "has_access": True,
            "course_id": course_id,
            "purchased_at": None  # Админы не покупают, у них всегда доступ
        }
    
    # Получаем пользователя по telegram_id (BIGINT в БД)
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    db_user = result.scalar_one_or_none()
    
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Проверяем наличие курса у пользователя
    result = await session.execute(
        select(UserCourse).where(
            UserCourse.user_id == db_user.id,
            UserCourse.course_id == course_id
        )
    )
    user_course = result.scalar_one_or_none()
    
    has_access = user_course is not None
    
    return {
        "has_access": has_access,
        "course_id": course_id,
        "purchased_at": user_course.purchased_at.isoformat() if user_course and user_course.purchased_at else None
    }

