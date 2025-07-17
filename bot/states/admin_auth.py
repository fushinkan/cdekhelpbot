from aiogram.fsm.state import StatesGroup, State


class AdminAuth(StatesGroup):
    """_
    Состояние для авторизации администартора в Telegram-боте.

    """
    phone = State()
    set_password = State()
    confirm_password = State()
    enter_password = State()