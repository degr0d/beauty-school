"""
Вспомогательные функции для регистрации пользователей
"""

from typing import Tuple, Optional
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton,
    WebAppInfo
)
from backend.config import settings


def get_consent_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру для согласия на обработку данных"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Согласен", callback_data="consent_agreed")],
        [InlineKeyboardButton(text="❌ Отказаться", callback_data="consent_declined")]
    ])


def get_phone_keyboard() -> ReplyKeyboardMarkup:
    """Создает клавиатуру для запроса телефона"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Поделиться контактом", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def get_webapp_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру с кнопкой Mini App"""
    # Получаем актуальный WEBAPP_URL с автоматической перезагрузкой
    from backend.config import get_webapp_url
    webapp_url = get_webapp_url()
    
    # Проверяем что URL HTTPS для Mini App
    if webapp_url.startswith('https://'):
        # Кнопка Mini App (Web App) - только для HTTPS
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="🚀 Открыть приложение",
                web_app=WebAppInfo(url=webapp_url)
            )]
        ])
    else:
        # Если нет HTTPS - показываем обычную ссылку
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="🚀 Открыть приложение",
                url=webapp_url
            )]
        ])


def get_consent_text() -> str:
    """Возвращает текст согласия на обработку данных"""
    return (
        "📋 <b>Согласие на обработку персональных данных</b>\n\n"
        "Мы будем использовать твои данные (ФИО, телефон) только для:\n"
        "✅ Связи по вопросам обучения\n"
        "✅ Выдачи сертификатов\n"
        "✅ Улучшения качества курсов\n\n"
        "Твои данные в безопасности и не передаются третьим лицам.\n\n"
        "<i>Нажимая «Согласен», ты принимаешь условия.</i>"
    )


def get_fullname_request_text() -> str:
    """Возвращает текст запроса ФИО"""
    return (
        "Отлично! 🎉\n\n"
        "Теперь давай познакомимся.\n"
        "Как тебя зовут? (ФИО полностью)\n\n"
        "<i>Например: Иванова Мария Сергеевна</i>"
    )


def get_phone_request_text(fullname: str) -> str:
    """Возвращает текст запроса телефона"""
    return (
        f"Приятно познакомиться, {fullname}! 👋\n\n"
        "Теперь поделись своим номером телефона.\n"
        "Можешь нажать кнопку ниже или ввести вручную.\n\n"
        "<i>Формат: +7 (XXX) XXX-XX-XX</i>"
    )


def get_registration_success_text(fullname: str) -> str:
    """Возвращает текст успешной регистрации"""
    return (
        "✅ <b>Регистрация завершена!</b>\n\n"
        f"Отлично, {fullname}! Теперь ты часть нашей бьюти-школы 🎓\n\n"
        "Открывай приложение и начинай обучение! 📱"
    )


def get_consent_declined_text() -> str:
    """Возвращает текст при отказе от согласия"""
    return (
        "Жаль, что ты отказался 😔\n\n"
        "Без согласия мы не сможем зарегистрировать тебя в школе.\n"
        "Если передумаешь — нажми /start и начнем заново!"
    )


def validate_fullname(fullname: str) -> Tuple[bool, Optional[str]]:
    """
    Валидирует ФИО
    
    Returns:
        (is_valid, error_message)
    """
    fullname = fullname.strip()
    if len(fullname.split()) < 2:
        return False, (
            "❌ Пожалуйста, введи ФИО полностью (минимум Имя и Фамилия)\n\n"
            "<i>Например: Иванова Мария</i>"
        )
    return True, None


def validate_phone(phone: str) -> Tuple[bool, Optional[str]]:
    """
    Валидирует телефон
    
    Returns:
        (is_valid, error_message)
    """
    phone = phone.strip()
    # Удаляем все нецифровые символы кроме +
    cleaned = phone.replace("+", "").replace("-", "").replace("(", "").replace(")", "").replace(" ", "")
    
    if not cleaned.isdigit():
        return False, (
            "❌ Некорректный формат телефона\n\n"
            "Попробуй ещё раз или нажми кнопку «Поделиться контактом»"
        )
    return True, None

