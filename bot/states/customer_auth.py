from aiogram.fsm.state import StatesGroup, State


class CustomerAuth(StatesGroup):
    """_
    Состояние для авторизации простого пользователя в Telegram-боте.
    """
    
    choose_password_option = State()
    set_password = State()
    enter_password = State()