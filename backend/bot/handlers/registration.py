"""
Обработчик процесса регистрации
FSM (Finite State Machine) для многошаговой регистрации
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from backend.database import async_session, User
from backend.bot.states import RegistrationStates
from backend.bot.utils.registration_helpers import (
    get_consent_keyboard, get_consent_text,
    get_fullname_request_text, get_phone_request_text,
    get_phone_keyboard, get_registration_success_text,
    get_consent_declined_text, get_webapp_keyboard,
    validate_fullname, validate_phone
)

router = Router()


# ========================================
# Шаг 1: Кнопка "Присоединиться"
# ========================================
@router.callback_query(F.data == "start_registration")
async def start_registration(callback: CallbackQuery, state: FSMContext):
    """
    Пользователь нажал "Присоединиться"
    Показываем согласие на обработку персональных данных
    """
    await callback.message.edit_text(
        get_consent_text(),
        reply_markup=get_consent_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


# ========================================
# Шаг 2: Согласие на обработку данных
# ========================================
@router.callback_query(F.data == "consent_agreed")
async def consent_agreed(callback: CallbackQuery, state: FSMContext):
    """
    Пользователь согласился с обработкой данных
    Переходим к запросу ФИО
    """
    await state.set_state(RegistrationStates.waiting_fullname)
    await callback.message.edit_text(
        get_fullname_request_text(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "consent_declined")
async def consent_declined(callback: CallbackQuery):
    """
    Пользователь отказался от обработки данных
    """
    await callback.message.edit_text(get_consent_declined_text())
    await callback.answer()


# ========================================
# Шаг 3: Получение ФИО
# ========================================
@router.message(RegistrationStates.waiting_fullname)
async def process_fullname(message: Message, state: FSMContext):
    """
    Пользователь ввёл ФИО
    Валидация и переход к запросу телефона
    """
    fullname = message.text.strip()
    is_valid, error_message = validate_fullname(fullname)
    
    if not is_valid:
        await message.answer(error_message, parse_mode="HTML")
        return
    
    # Сохраняем ФИО в FSM context
    await state.update_data(fullname=fullname)
    await state.set_state(RegistrationStates.waiting_phone)
    
    await message.answer(
        get_phone_request_text(fullname),
        reply_markup=get_phone_keyboard(),
        parse_mode="HTML"
    )


# ========================================
# Шаг 4: Получение телефона
# ========================================
@router.message(RegistrationStates.waiting_phone, F.contact)
async def process_phone_contact(message: Message, state: FSMContext):
    """
    Пользователь поделился контактом через кнопку
    """
    phone = message.contact.phone_number
    await finalize_registration(message, state, phone)


@router.message(RegistrationStates.waiting_phone, F.text)
async def process_phone_text(message: Message, state: FSMContext):
    """
    Пользователь ввёл телефон вручную
    """
    phone = message.text.strip()
    is_valid, error_message = validate_phone(phone)
    
    if not is_valid:
        await message.answer(error_message)
        return
    
    await finalize_registration(message, state, phone)


async def finalize_registration(message: Message, state: FSMContext, phone: str):
    """
    Финальный шаг: сохранение пользователя в БД
    """
    data = await state.get_data()
    fullname = data.get("fullname")
    telegram_id = message.from_user.id
    username = message.from_user.username
    
    # Сохраняем в БД
    async with async_session() as session:
        user = User(
            telegram_id=telegram_id,
            username=username,
            full_name=fullname,
            phone=phone,
            consent_personal_data=True
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
    
    # Очищаем FSM
    await state.clear()
    
    # Отправляем сообщения
    await message.answer(
        get_registration_success_text(fullname),
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="HTML"
    )
    
    await message.answer(
        "👇 Нажми на кнопку ниже, чтобы открыть приложение:",
        reply_markup=get_webapp_keyboard()
    )


# ========================================
# Пример флоу регистрации:
# ========================================
# 1. /start (новый пользователь)
# 2. Кнопка "Присоединиться"
# 3. Согласие на обработку данных
# 4. Ввод ФИО (FSM: WAITING_FULLNAME)
# 5. Ввод телефона (FSM: WAITING_PHONE)
# 6. Сохранение в БД
# 7. Кнопка "Открыть приложение"

