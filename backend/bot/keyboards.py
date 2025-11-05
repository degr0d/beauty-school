"""
Клавиатуры для Telegram-бота
Inline и Reply клавиатуры
"""

from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    WebAppInfo
)


# ========================================
# Inline клавиатуры
# ========================================

def get_welcome_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура приветствия (кнопка "Присоединиться")
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✨ Присоединиться", callback_data="start_registration")]
    ])


def get_consent_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура согласия на обработку данных
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Согласен", callback_data="consent_agreed")],
        [InlineKeyboardButton(text="❌ Отказаться", callback_data="consent_declined")]
    ])


def get_webapp_keyboard(url: str = "https://yourdomain.com") -> InlineKeyboardMarkup:
    """
    Клавиатура с кнопкой открытия Mini App
    
    Args:
        url: URL Mini App
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📱 Открыть приложение",
            web_app=WebAppInfo(url=url)
        )]
    ])


# ========================================
# Reply клавиатуры
# ========================================

def get_phone_keyboard() -> ReplyKeyboardMarkup:
    """
    Клавиатура с кнопкой "Поделиться контактом"
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Поделиться контактом", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """
    Главное меню (опционально, если нужно)
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📚 Курсы"), KeyboardButton(text="👤 Профиль")],
            [KeyboardButton(text="💬 Сообщества"), KeyboardButton(text="❓ Помощь")]
        ],
        resize_keyboard=True
    )


# ========================================
# Использование в коде:
# ========================================
# from backend.bot.keyboards import get_welcome_keyboard
# 
# await message.answer("Привет!", reply_markup=get_welcome_keyboard())

