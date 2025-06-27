from aiogram.fsm.state import StatesGroup, State


class AdminAuth(StatesGroup):
    """_
    Состояние для авторизации администартора в Telegram-боте.

    """
    
    waiting_for_phone = State()
    waiting_for_password = State()