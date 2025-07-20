from aiogram.fsm.state import StatesGroup, State


class Auth(StatesGroup):
    """
    Общая группа состояний для процесса авторизации в Telegram-боте.

    Атрибуты:
        waiting_for_phone (State): Ожидание ввода номера телефона пользователем.
    """
    
    waiting_for_phone = State()
