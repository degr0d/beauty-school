"""
FSM (Finite State Machine) состояния для бота
Используются в многошаговых диалогах (например, регистрация)
"""

from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    """
    Состояния процесса регистрации
    """
    waiting_fullname = State()  # Ожидание ввода ФИО
    waiting_phone = State()     # Ожидание ввода телефона


# ========================================
# Пример других состояний (для будущих фич)
# ========================================

class CourseCreationStates(StatesGroup):
    """
    Состояния создания курса (для админ-бота)
    """
    waiting_title = State()
    waiting_description = State()
    waiting_category = State()
    waiting_cover = State()


# ========================================
# Использование в коде:
# ========================================
# from backend.bot.states import RegistrationStates
# 
# @router.message(F.text)
# async def handle_fullname(message: Message, state: FSMContext):
#     await state.set_state(RegistrationStates.waiting_fullname)
#     ...

