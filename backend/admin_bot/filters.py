"""
Фильтры для админ-бота
"""

from aiogram.filters import BaseFilter
from aiogram.types import Message
from typing import Any

from backend.config import settings


class AdminFilter(BaseFilter):
    """
    Фильтр для проверки, является ли пользователь админом
    """
    
    async def __call__(self, message: Message, **kwargs: Any) -> bool:
        """
        Проверяет, является ли пользователь админом
        
        Args:
            message: Сообщение от пользователя
            
        Returns:
            True если пользователь админ, False иначе
        """
        return message.from_user.id in settings.admin_ids_list

