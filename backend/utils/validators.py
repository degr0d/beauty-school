"""
Валидаторы данных
"""

import re


def validate_phone(phone: str) -> bool:
    """
    Валидация номера телефона
    
    Args:
        phone: Номер телефона
    
    Returns:
        bool: True если валиден
    """
    # Убираем все символы кроме цифр и +
    cleaned = re.sub(r'[^\d+]', '', phone)
    
    # Проверяем длину (минимум 10 цифр)
    if len(cleaned.replace("+", "")) < 10:
        return False
    
    return True


def validate_fullname(fullname: str) -> bool:
    """
    Валидация ФИО
    
    Args:
        fullname: ФИО
    
    Returns:
        bool: True если валиден (минимум 2 слова)
    """
    words = fullname.strip().split()
    return len(words) >= 2


def validate_email(email: str) -> bool:
    """
    Валидация email (опционально, для будущих фич)
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


# ========================================
# Использование:
# ========================================
# from backend.utils.validators import validate_phone, validate_fullname
# 
# if not validate_phone(phone):
#     raise ValueError("Некорректный номер телефона")

