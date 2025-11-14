"""
API эндпоинты для поддержки
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from datetime import datetime

from backend.database import get_session, SupportTicket, SupportMessage, User
from backend.webapp.middleware import get_telegram_user
from backend.config import settings
from backend.services.notifications import send_notification

router = APIRouter()


# ========================================
# Схемы
# ========================================
class SupportMessageResponse(BaseModel):
    id: int
    ticket_id: int
    message: str
    is_from_admin: bool
    created_at: str
    
    class Config:
        from_attributes = True


class SupportTicketResponse(BaseModel):
    id: int
    subject: Optional[str]
    status: str
    created_at: str
    updated_at: str
    messages: List[SupportMessageResponse]
    
    class Config:
        from_attributes = True


class CreateTicketRequest(BaseModel):
    subject: Optional[str] = None
    message: str


class SendMessageRequest(BaseModel):
    message: str


# ========================================
# Эндпоинты
# ========================================
@router.get("/ticket", response_model=SupportTicketResponse)
async def get_my_ticket(
    user: dict = Depends(get_telegram_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Получить активный тикет пользователя (или создать новый)
    """
    telegram_id = int(user["id"])
    
    # Получаем пользователя
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    db_user = result.scalar_one_or_none()
    
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Ищем открытый тикет
    result = await session.execute(
        select(SupportTicket)
        .where(
            SupportTicket.user_id == db_user.id,
            SupportTicket.status == "open"
        )
        .order_by(desc(SupportTicket.created_at))
        .limit(1)
    )
    ticket = result.scalar_one_or_none()
    
    # Если нет открытого тикета - создаем новый
    if not ticket:
        ticket = SupportTicket(
            user_id=db_user.id,
            subject="Вопрос в поддержку",
            status="open"
        )
        session.add(ticket)
        await session.commit()
        await session.refresh(ticket)
    
    # Загружаем сообщения
    result = await session.execute(
        select(SupportMessage)
        .where(SupportMessage.ticket_id == ticket.id)
        .order_by(SupportMessage.created_at)
    )
    messages = result.scalars().all()
    
    # Формируем ответ
    return SupportTicketResponse(
        id=ticket.id,
        subject=ticket.subject,
        status=ticket.status,
        created_at=ticket.created_at.isoformat() if hasattr(ticket.created_at, 'isoformat') else str(ticket.created_at),
        updated_at=ticket.updated_at.isoformat() if hasattr(ticket.updated_at, 'isoformat') else str(ticket.updated_at),
        messages=[
            SupportMessageResponse(
                id=msg.id,
                ticket_id=msg.ticket_id,
                message=msg.message,
                is_from_admin=msg.is_from_admin,
                created_at=msg.created_at.isoformat() if hasattr(msg.created_at, 'isoformat') else str(msg.created_at)
            )
            for msg in messages
        ]
    )


@router.post("/ticket", response_model=SupportTicketResponse)
async def create_ticket(
    request: CreateTicketRequest,
    user: dict = Depends(get_telegram_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Создать новый тикет поддержки
    """
    telegram_id = int(user["id"])
    
    # Получаем пользователя
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    db_user = result.scalar_one_or_none()
    
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Создаем тикет
    ticket = SupportTicket(
        user_id=db_user.id,
        subject=request.subject or "Вопрос в поддержку",
        status="open"
    )
    session.add(ticket)
    await session.commit()
    await session.refresh(ticket)
    
    # Добавляем первое сообщение
    if request.message:
        message = SupportMessage(
            ticket_id=ticket.id,
            user_id=db_user.id,
            message=request.message,
            is_from_admin=False
        )
        session.add(message)
        await session.commit()
        
        # Отправляем уведомление админам
        await notify_admins_new_ticket(db_user, ticket, request.message)
    
    return SupportTicketResponse(
        id=ticket.id,
        subject=ticket.subject,
        status=ticket.status,
        created_at=ticket.created_at.isoformat() if hasattr(ticket.created_at, 'isoformat') else str(ticket.created_at),
        updated_at=ticket.updated_at.isoformat() if hasattr(ticket.updated_at, 'isoformat') else str(ticket.updated_at),
        messages=[]
    )


@router.post("/ticket/message", response_model=SupportMessageResponse)
async def send_message(
    request: SendMessageRequest,
    user: dict = Depends(get_telegram_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Отправить сообщение в тикет поддержки
    """
    telegram_id = int(user["id"])
    
    # Получаем пользователя
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    db_user = result.scalar_one_or_none()
    
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Получаем или создаем открытый тикет
    result = await session.execute(
        select(SupportTicket)
        .where(
            SupportTicket.user_id == db_user.id,
            SupportTicket.status == "open"
        )
        .order_by(desc(SupportTicket.created_at))
        .limit(1)
    )
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        # Создаем новый тикет
        ticket = SupportTicket(
            user_id=db_user.id,
            subject="Вопрос в поддержку",
            status="open"
        )
        session.add(ticket)
        await session.commit()
        await session.refresh(ticket)
    
    # Создаем сообщение
    message = SupportMessage(
        ticket_id=ticket.id,
        user_id=db_user.id,
        message=request.message,
        is_from_admin=False
    )
    session.add(message)
    
    # Обновляем updated_at тикета
    ticket.updated_at = datetime.now()
    
    await session.commit()
    await session.refresh(message)
    
    # Отправляем уведомление админам
    await notify_admins_new_message(db_user, ticket, request.message)
    
    return SupportMessageResponse(
        id=message.id,
        ticket_id=message.ticket_id,
        message=message.message,
        is_from_admin=message.is_from_admin,
        created_at=message.created_at.isoformat() if hasattr(message.created_at, 'isoformat') else str(message.created_at)
    )


async def notify_admins_new_ticket(user: User, ticket: SupportTicket, first_message: str):
    """
    Уведомить админов о новом тикете
    """
    try:
        for admin_id in settings.admin_ids_list:
            message_text = (
                f"🆕 <b>Новый тикет поддержки</b>\n\n"
                f"👤 Пользователь: {user.full_name}\n"
                f"🆔 Telegram ID: <code>{user.telegram_id}</code>\n"
                f"📋 Тикет: #{ticket.id}\n\n"
                f"💬 Сообщение:\n{first_message}\n\n"
                f"💡 Ответьте пользователю через админ-бота"
            )
            await send_notification(admin_id, message_text)
    except Exception as e:
        print(f"⚠️ Ошибка отправки уведомления админам о новом тикете: {e}")


async def notify_admins_new_message(user: User, ticket: SupportTicket, message_text: str):
    """
    Уведомить админов о новом сообщении в тикете
    """
    try:
        for admin_id in settings.admin_ids_list:
            notification = (
                f"💬 <b>Новое сообщение в тикете #{ticket.id}</b>\n\n"
                f"👤 Пользователь: {user.full_name}\n"
                f"🆔 Telegram ID: <code>{user.telegram_id}</code>\n\n"
                f"💬 Сообщение:\n{message_text}\n\n"
                f"💡 Ответьте пользователю через админ-бота"
            )
            await send_notification(admin_id, notification)
    except Exception as e:
        print(f"⚠️ Ошибка отправки уведомления админам о новом сообщении: {e}")

