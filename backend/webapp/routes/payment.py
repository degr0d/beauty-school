"""
API эндпоинты для оплаты через ЮKassa
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from backend.database import get_session, User, Course, Payment, UserCourse
from backend.webapp.middleware import get_telegram_user
from backend.config import settings

router = APIRouter()


# ========================================
# Схемы запросов/ответов
# ========================================
class CreatePaymentRequest(BaseModel):
    course_id: int


class CreatePaymentResponse(BaseModel):
    payment_id: int
    payment_url: str
    amount: float
    status: str


class PaymentStatusResponse(BaseModel):
    payment_id: int
    status: str
    amount: float
    course_id: int


# ========================================
# Эндпоинты
# ========================================
@router.post("/create", response_model=CreatePaymentResponse)
async def create_payment(
    request: CreatePaymentRequest,
    user: dict = Depends(get_telegram_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Создать платеж для курса
    
    TODO: Когда появятся данные ЮKassa:
    1. Раскомментировать импорт: from yookassa import Configuration, Payment as YooPayment
    2. Настроить Configuration.account_id и Configuration.secret_key
    3. Создать платеж через YooPayment.create()
    4. Сохранить yookassa_payment_id в БД
    5. Вернуть confirmation_url для оплаты
    """
    telegram_id = user["id"]
    
    # Проверяем что пользователь существует
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    db_user = result.scalar_one_or_none()
    
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Проверяем что курс существует
    result = await session.execute(
        select(Course).where(Course.id == request.course_id)
    )
    course = result.scalar_one_or_none()
    
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Проверяем что пользователь ещё не купил курс
    result = await session.execute(
        select(UserCourse).where(
            UserCourse.user_id == db_user.id,
            UserCourse.course_id == request.course_id
        )
    )
    existing_purchase = result.scalar_one_or_none()
    
    if existing_purchase:
        raise HTTPException(
            status_code=400,
            detail="Course already purchased"
        )
    
    # Проверяем что ЮKassa настроена
    if not settings.YUKASSA_SHOP_ID or not settings.YUKASSA_SECRET_KEY:
        raise HTTPException(
            status_code=503,
            detail="Payment system is not configured. Please contact support."
        )
    
    # Создаём запись о платеже в БД
    payment = Payment(
        user_id=db_user.id,
        course_id=request.course_id,
        amount=course.price,
        status="pending"
    )
    session.add(payment)
    await session.commit()
    await session.refresh(payment)
    
    # Интеграция с ЮKassa
    try:
        from yookassa import Configuration, Payment as YooPayment
        
        # Настройка ЮKassa
        Configuration.account_id = settings.YUKASSA_SHOP_ID
        Configuration.secret_key = settings.YUKASSA_SECRET_KEY
        
        # Создание платежа
        payment_data = {
            "amount": {
                "value": str(float(course.price)),
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": settings.YUKASSA_RETURN_URL or f"{settings.WEBAPP_URL}/payment/success?payment_id={payment.id}"
            },
            "capture": True,
            "description": f"Оплата курса: {course.title}",
            "metadata": {
                "user_id": str(db_user.id),
                "course_id": str(course.id),
                "payment_id": str(payment.id)
            }
        }
        
        yoo_payment = YooPayment.create(payment_data)
        
        # Сохраняем ID платежа ЮKassa
        payment.yookassa_payment_id = yoo_payment.id
        await session.commit()
        
        return CreatePaymentResponse(
            payment_id=payment.id,
            payment_url=yoo_payment.confirmation.confirmation_url,
            amount=float(course.price),
            status="pending"
        )
    except Exception as e:
        # Если интеграция не настроена или произошла ошибка - используем заглушку
        print(f"⚠️ [Payment] Ошибка интеграции с ЮKassa: {e}")
        print(f"   Используется заглушка для разработки")
        # В режиме разработки возвращаем заглушку
        return CreatePaymentResponse(
            payment_id=payment.id,
            payment_url=f"{settings.WEBAPP_URL or 'http://localhost:5173'}/payment/success?payment_id={payment.id}",
            amount=float(course.price),
            status="pending"
        )


@router.get("/status/{payment_id}", response_model=PaymentStatusResponse)
async def get_payment_status(
    payment_id: int,
    user: dict = Depends(get_telegram_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Получить статус платежа
    
    TODO: Когда появятся данные ЮKassa:
    1. Раскомментировать импорт: from yookassa import Payment as YooPayment
    2. Получить статус через YooPayment.find_one(yookassa_payment_id)
    3. Обновить статус в БД
    4. Если оплачено - создать запись UserCourse
    """
    telegram_id = user["id"]
    
    # Получаем пользователя
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    db_user = result.scalar_one_or_none()
    
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Получаем платеж
    result = await session.execute(
        select(Payment).where(
            Payment.id == payment_id,
            Payment.user_id == db_user.id
        )
    )
    payment = result.scalar_one_or_none()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Проверка статуса в ЮKassa
    if payment.yookassa_payment_id and settings.YUKASSA_SHOP_ID and settings.YUKASSA_SECRET_KEY:
        try:
            from yookassa import Configuration, Payment as YooPayment
            from datetime import datetime
            
            # Настройка ЮKassa
            Configuration.account_id = settings.YUKASSA_SHOP_ID
            Configuration.secret_key = settings.YUKASSA_SECRET_KEY
            
            # Получаем актуальный статус платежа
            yoo_payment = YooPayment.find_one(payment.yookassa_payment_id)
            
            # Обновляем статус если изменился
            if yoo_payment.status == "succeeded" and payment.status != "succeeded":
                payment.status = "succeeded"
                payment.paid_at = datetime.now()
                payment.payment_method = yoo_payment.payment_method.type if yoo_payment.payment_method else None
                
                # Проверяем, не создана ли уже запись UserCourse
                result = await session.execute(
                    select(UserCourse).where(
                        UserCourse.user_id == db_user.id,
                        UserCourse.course_id == payment.course_id
                    )
                )
                existing_user_course = result.scalar_one_or_none()
                
                # Создаём запись о покупке курса, если её ещё нет
                if not existing_user_course:
                    user_course = UserCourse(
                        user_id=db_user.id,
                        course_id=payment.course_id
                    )
                    session.add(user_course)
                    print(f"✅ [Payment] Создана запись UserCourse для пользователя {db_user.id} и курса {payment.course_id}")
                
                await session.commit()
                print(f"✅ [Payment] Платеж {payment.id} обновлен: статус = succeeded")
                
            elif yoo_payment.status == "canceled" and payment.status != "canceled":
                payment.status = "canceled"
                await session.commit()
                print(f"⚠️ [Payment] Платеж {payment.id} отменен")
                
        except Exception as e:
            print(f"⚠️ [Payment] Ошибка проверки статуса в ЮKassa: {e}")
            # Продолжаем с текущим статусом из БД
    
    return PaymentStatusResponse(
        payment_id=payment.id,
        status=payment.status,
        amount=float(payment.amount),
        course_id=payment.course_id
    )


@router.post("/webhook")
async def payment_webhook(
    request_data: dict,
    session: AsyncSession = Depends(get_session)
):
    """
    Webhook для уведомлений от ЮKassa
    
    Обрабатывает события:
    - payment.succeeded - платеж успешно завершен
    - payment.canceled - платеж отменен
    
    Примечание: В настройках ЮKassa нужно указать URL этого webhook
    """
    from datetime import datetime
    
    try:
        # Парсим событие из JSON body
        event_type = request_data.get("event")
        payment_object = request_data.get("object", {})
        
        if not event_type or not payment_object:
            print("⚠️ [Webhook] Неверный формат запроса")
            return {"status": "error", "message": "Invalid request format"}
        
        # Получаем ID платежа ЮKassa
        yookassa_payment_id = payment_object.get("id")
        if not yookassa_payment_id:
            print("⚠️ [Webhook] Отсутствует ID платежа")
            return {"status": "error", "message": "Missing payment ID"}
        
        # Ищем платеж в БД
        result = await session.execute(
            select(Payment).where(Payment.yookassa_payment_id == yookassa_payment_id)
        )
        payment = result.scalar_one_or_none()
        
        if not payment:
            print(f"⚠️ [Webhook] Платеж с yookassa_payment_id={yookassa_payment_id} не найден в БД")
            return {"status": "error", "message": "Payment not found"}
        
        # Обрабатываем событие
        if event_type == "payment.succeeded":
            if payment.status != "succeeded":
                payment.status = "succeeded"
                payment.paid_at = datetime.now()
                payment.payment_method = payment_object.get("payment_method", {}).get("type") if payment_object.get("payment_method") else None
                
                # Получаем пользователя
                result = await session.execute(
                    select(User).where(User.id == payment.user_id)
                )
                db_user = result.scalar_one_or_none()
                
                if db_user:
                    # Проверяем, не создана ли уже запись UserCourse
                    result = await session.execute(
                        select(UserCourse).where(
                            UserCourse.user_id == db_user.id,
                            UserCourse.course_id == payment.course_id
                        )
                    )
                    existing_user_course = result.scalar_one_or_none()
                    
                    # Создаём запись о покупке курса, если её ещё нет
                    if not existing_user_course:
                        user_course = UserCourse(
                            user_id=db_user.id,
                            course_id=payment.course_id
                        )
                        session.add(user_course)
                        print(f"✅ [Webhook] Создана запись UserCourse для пользователя {db_user.id} и курса {payment.course_id}")
                
                await session.commit()
                print(f"✅ [Webhook] Платеж {payment.id} обработан: статус = succeeded")
                
        elif event_type == "payment.canceled":
            if payment.status != "canceled":
                payment.status = "canceled"
                await session.commit()
                print(f"⚠️ [Webhook] Платеж {payment.id} отменен")
        
        return {"status": "ok"}
        
    except Exception as e:
        print(f"❌ [Webhook] Ошибка обработки webhook: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}


@router.get("/history")
async def get_payment_history(
    user: dict = Depends(get_telegram_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Получить историю платежей пользователя
    """
    telegram_id = user["id"]
    
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    db_user = result.scalar_one_or_none()
    
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    result = await session.execute(
        select(Payment, Course)
        .join(Course, Payment.course_id == Course.id)
        .where(Payment.user_id == db_user.id)
        .order_by(Payment.created_at.desc())
    )
    payments = result.all()
    
    return [
        {
            "id": payment.id,
            "course_id": course.id,
            "course_title": course.title,
            "amount": float(payment.amount),
            "status": payment.status,
            "created_at": payment.created_at.isoformat() if payment.created_at else None,
            "paid_at": payment.paid_at.isoformat() if payment.paid_at else None
        }
        for payment, course in payments
    ]

