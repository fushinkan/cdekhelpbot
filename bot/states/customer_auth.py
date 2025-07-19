from aiogram.fsm.state import StatesGroup, State


class CustomerAuth(StatesGroup):
    """_
    Состояние для авторизации простого пользователя в Telegram-боте.
    """
    phone = State()
    set_password = State()
    confirm_password = State()
    enter_password = State()
    main_menu = State()