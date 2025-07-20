from aiogram.fsm.state import StatesGroup, State

class AdminAuth(StatesGroup):
    """
    Состояния для процесса авторизации администратора.

    Наследуется от:
        StatesGroup: базовый класс для описания состояний в FSM.
        
    Атрибуты:
        phone (State): Ввод номера телефона администратора.
        set_password (State): Установка нового пароля администратора.
        confirm_password (State): Подтверждение установленного пароля.
        enter_password (State): Ввод существующего пароля для входа администратора.
    """
    
    phone = State()
    set_password = State()
    confirm_password = State()
    enter_password = State()