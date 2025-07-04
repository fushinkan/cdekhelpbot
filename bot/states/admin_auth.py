from aiogram.fsm.state import StatesGroup, State


class AdminAuth(StatesGroup):
    """_
    Состояние для авторизации администартора в Telegram-боте.

    """
    
    password = State()