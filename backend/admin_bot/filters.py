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
        user_id = message.from_user.id
        admin_ids = settings.admin_ids_list
        
        # Логирование для диагностики
        print(f"🔍 [AdminFilter] Проверка доступа для user_id={user_id}")
        print(f"🔍 [AdminFilter] ADMIN_IDS из настроек: {settings.ADMIN_IDS}")
        print(f"🔍 [AdminFilter] admin_ids_list: {admin_ids}")
        print(f"🔍 [AdminFilter] Пользователь админ? {user_id in admin_ids}")
        
        is_admin = user_id in admin_ids
        
        if not is_admin:
            print(f"⚠️ [AdminFilter] Доступ запрещен для user_id={user_id}")
            print(f"   Доступные админы: {admin_ids}")
        
        return is_admin

