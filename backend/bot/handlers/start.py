"""
Обработчик команды /start
Приветствие и проверка регистрации
"""

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from sqlalchemy import select

from backend.database import async_session, User
from backend.config import get_webapp_url

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    """
    Обработка команды /start
    
    Логика:
    1. Проверяем, зарегистрирован ли пользователь (есть ли в БД)
    2. Если ДА -> показываем кнопку "Открыть приложение"
    3. Если НЕТ -> показываем приветствие + кнопка "Присоединиться"
    """
    telegram_id = message.from_user.id
    
    # Проверяем, есть ли пользователь в БД
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
    
    if user:
        # Пользователь уже зарегистрирован
        await send_webapp_button(message, user.full_name)
    else:
        # Новый пользователь - показываем онбординг
        await send_welcome_message(message)


async def send_welcome_message(message: Message):
    """
    Отправляет приветственное сообщение новому пользователю
    """
    welcome_text = (
        "🎉 <b>Добро пожаловать в бьюти-школу!</b>\n\n"
        "Здесь ты найдешь курсы по:\n"
        "💅 Маникюру и педикюру\n"
        "👁 Ресницам и бровям\n"
        "🦶 Подологии\n"
        "💼 Своё дело и маркетинг\n\n"
        "Начнем? 🚀"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✨ Присоединиться", callback_data="start_registration")]
    ])
    
    await message.answer(welcome_text, reply_markup=keyboard, parse_mode="HTML")


async def send_webapp_button(message: Message, user_name: str):
    """
    Отправляет приветствие зарегистрированному пользователю
    с кнопкой Mini App
    """
    # Получаем актуальный WEBAPP_URL с автоматической перезагрузкой
    webapp_url = get_webapp_url()
    
    text = (
        f"Привет, {user_name}! 👋\n\n"
        "Рада видеть тебя снова! Открывай приложение и продолжай обучение 📚"
    )
    
    # Проверяем что URL HTTPS для Mini App
    if webapp_url.startswith('https://'):
        # Кнопка Mini App (Web App) - только для HTTPS
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="🚀 Открыть приложение",
                web_app=WebAppInfo(url=webapp_url)
            )],
            [InlineKeyboardButton(text="📚 Мои курсы", callback_data="my_courses")],
            [InlineKeyboardButton(text="👤 Профиль", callback_data="my_profile")],
            [InlineKeyboardButton(text="❓ Помощь", callback_data="help")]
        ])
    else:
        # Если нет HTTPS - показываем обычную ссылку
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="🚀 Открыть приложение",
                url=webapp_url
            )],
            [InlineKeyboardButton(text="📚 Мои курсы", callback_data="my_courses")],
            [InlineKeyboardButton(text="👤 Профиль", callback_data="my_profile")],
            [InlineKeyboardButton(text="❓ Помощь", callback_data="help")]
        ])
        text += f"\n\n⚠️ <i>Примечание: Туннель не запущен. Откройте в браузере: {webapp_url}</i>"
    
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")


# ========================================
# Пример callback для кнопки "Присоединиться"
# (обрабатывается в registration.py)
# ========================================

