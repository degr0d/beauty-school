"""
API эндпоинты для управления уведомлениями (админ)
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from backend.database import get_session
from backend.webapp.middleware import get_telegram_user
from backend.config import settings
from backend.services.notifications import broadcast_notification

router = APIRouter()


# ========================================
# Схемы запросов
# ========================================
class BroadcastRequest(BaseModel):
    message: str
    user_ids: Optional[list[int]] = None  # Если None - всем активным пользователям


# ========================================
# Эндпоинты
# ========================================
@router.post("/broadcast")
async def send_broadcast(
    request: BroadcastRequest,
    user: dict = Depends(get_telegram_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Отправить массовое уведомление пользователям
    Только для админов
    """
    # Проверяем, что пользователь админ
    telegram_id = user["id"]
    is_admin = telegram_id in settings.admin_ids_list
    
    if not is_admin:
        raise HTTPException(status_code=403, detail="Only admins can send broadcasts")
    
    # Отправляем уведомления
    result = await broadcast_notification(
        session,
        request.message,
        request.user_ids
    )
    
    return {
        "status": "success",
        "message": "Broadcast sent",
        "result": result
    }

