"""
Обработчик для работы с Telegram Mini App
"""

from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters import Command
from backend.config import get_webapp_url

router = Router()


@router.message(Command("app"))
async def open_webapp(message: Message):
    """
    Команда /app - открыть Mini App
    """
    # Получаем актуальный WEBAPP_URL с автоматической перезагрузкой
    webapp_url = get_webapp_url()
    
    # Проверяем что URL HTTPS для Mini App
    if webapp_url.startswith('https://'):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="📱 Открыть приложение",
                web_app=WebAppInfo(url=webapp_url)
            )]
        ])
        text = "Нажми на кнопку ниже, чтобы открыть приложение 👇"
    else:
        # Если нет HTTPS - показываем обычную ссылку
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="📱 Открыть приложение",
                url=webapp_url
            )]
        ])
        text = f"⚠️ Туннель не запущен. Откройте в браузере:\n{webapp_url}"
    
    await message.answer(text, reply_markup=keyboard)


# ========================================
# Дополнительные команды (опционально)
# ========================================

@router.message(Command("help"))
async def cmd_help(message: Message):
    """
    Команда /help - помощь
    """
    help_text = (
        "📚 <b>Доступные команды:</b>\n\n"
        "/start - Начать работу с ботом\n"
        "/app - Открыть приложение\n"
        "/profile - Мой профиль\n"
        "/help - Помощь\n\n"
        "Если возникли вопросы, пиши в поддержку: @your_support"
    )
    
    await message.answer(help_text, parse_mode="HTML")


@router.message(Command("profile"))
async def cmd_profile(message: Message):
    """
    Команда /profile - открыть профиль в Mini App
    """
    # Получаем актуальный WEBAPP_URL с автоматической перезагрузкой
    base_url = get_webapp_url()
    webapp_url = f"{base_url}/profile"
    
    # Проверяем что URL HTTPS для Mini App
    if base_url.startswith('https://'):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="👤 Мой профиль",
                web_app=WebAppInfo(url=webapp_url)
            )]
        ])
        text = "Открой свой профиль в приложении:"
    else:
        # Если нет HTTPS - показываем обычную ссылку
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="👤 Мой профиль",
                url=webapp_url
            )]
        ])
        text = f"⚠️ Туннель не запущен. Откройте в браузере:\n{webapp_url}"
    
    await message.answer(text, reply_markup=keyboard)

