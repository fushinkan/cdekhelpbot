from aiogram.fsm.state import StatesGroup, State


class CustomerAuth(StatesGroup):
    """
    Состояния для процесса авторизации пользователя.

    Наследуется от:
        StatesGroup: Базовый класс для описания состояний в FSM.
        
    Атрибуты:
        phone (State): Ввод номера телефона пользователя.
        set_password (State): Установка нового пароля.
        confirm_password (State): Подтверждение установленного пароля.
        enter_password (State): Ввод существующего пароля для входа.
        main_menu (State): Основное меню после успешной авторизации.
    """
    
    phone = State()
    set_password = State()
    confirm_password = State()
    enter_password = State()
    main_menu = State()