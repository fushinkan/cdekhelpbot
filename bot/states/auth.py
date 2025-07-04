from aiogram.fsm.state import StatesGroup, State


class Auth(StatesGroup):
    """_
    Общая точка входа для определения состояния авторизации в Telegram-боте.

    """
    
    waiting_for_phone = State()
