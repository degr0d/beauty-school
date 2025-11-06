"""
Обработчик команды /start
Приветствие и проверка регистрации
"""

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
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
# Обработчики callback для кнопок меню
# ========================================

@router.callback_query(F.data == "my_courses")
async def callback_my_courses(callback: CallbackQuery):
    """
    Обработчик кнопки "Мои курсы"
    Открывает Mini App на странице курсов
    """
    telegram_id = callback.from_user.id
    
    # Проверяем, зарегистрирован ли пользователь
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
    
    if not user:
        await callback.answer("❌ Ты ещё не зарегистрирован! Нажми /start", show_alert=True)
        return
    
    # Получаем URL Mini App
    base_url = get_webapp_url()
    webapp_url = f"{base_url}/courses"
    
    # Проверяем что URL HTTPS для Mini App
    if base_url.startswith('https://'):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="📚 Открыть мои курсы",
                web_app=WebAppInfo(url=webapp_url)
            )]
        ])
        text = "📚 <b>Мои курсы</b>\n\nОткрой приложение, чтобы посмотреть свои курсы:"
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="📚 Открыть мои курсы",
                url=webapp_url
            )]
        ])
        text = f"📚 <b>Мои курсы</b>\n\n⚠️ Откройте в браузере:\n{webapp_url}"
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "my_profile")
async def callback_my_profile(callback: CallbackQuery):
    """
    Обработчик кнопки "Профиль"
    Открывает Mini App на странице профиля
    """
    telegram_id = callback.from_user.id
    
    # Проверяем, зарегистрирован ли пользователь
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
    
    if not user:
        await callback.answer("❌ Ты ещё не зарегистрирован! Нажми /start", show_alert=True)
        return
    
    # Получаем URL Mini App
    base_url = get_webapp_url()
    webapp_url = f"{base_url}/profile"
    
    # Проверяем что URL HTTPS для Mini App
    if base_url.startswith('https://'):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="👤 Открыть профиль",
                web_app=WebAppInfo(url=webapp_url)
            )]
        ])
        text = "👤 <b>Мой профиль</b>\n\nОткрой приложение, чтобы посмотреть и отредактировать свой профиль:"
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="👤 Открыть профиль",
                url=webapp_url
            )]
        ])
        text = f"👤 <b>Мой профиль</b>\n\n⚠️ Откройте в браузере:\n{webapp_url}"
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "help")
async def callback_help(callback: CallbackQuery):
    """
    Обработчик кнопки "Помощь"
    Показывает справку по командам
    """
    help_text = (
        "❓ <b>Помощь</b>\n\n"
        "📚 <b>Доступные команды:</b>\n"
        "/start - Главное меню\n"
        "/app - Открыть приложение\n"
        "/profile - Мой профиль\n"
        "/courses - Список всех курсов\n"
        "/help - Эта справка\n\n"
        "💡 <b>Совет:</b> Используй кнопки в меню для быстрого доступа к функциям!\n\n"
        "<i>Если возникли вопросы, пиши в поддержку!</i>"
    )
    
    # Кнопка "Назад" для возврата в главное меню
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_menu")]
    ])
    
    await callback.message.edit_text(help_text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "back_to_menu")
async def callback_back_to_menu(callback: CallbackQuery):
    """
    Обработчик кнопки "Назад в меню"
    Возвращает пользователя в главное меню
    """
    telegram_id = callback.from_user.id
    
    # Проверяем, зарегистрирован ли пользователь
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
    
    if not user:
        await callback.answer("❌ Ты ещё не зарегистрирован! Нажми /start", show_alert=True)
        return
    
    # Возвращаем главное меню (редактируем сообщение)
    webapp_url = get_webapp_url()
    text = (
        f"Привет, {user.full_name}! 👋\n\n"
        "Рада видеть тебя снова! Открывай приложение и продолжай обучение 📚"
    )
    
    # Проверяем что URL HTTPS для Mini App
    if webapp_url.startswith('https://'):
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
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

