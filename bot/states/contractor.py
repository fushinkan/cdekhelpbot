from aiogram.fsm.state import StatesGroup, State

from bot.keyboards.backbuttons import BackButtons

class Contractor(StatesGroup):
    """
    Состояния для процесса сбора данных нового контрагента.

    Args:
        StatesGroup: базовый класс для описания состояний в FSM.
        
    Атрибуты:
        phone (State): Ввод номера телефона контрагента.
        tin (State): Ввод ИНН контрагента.
    """
    
    phone = State()
    tin = State()

    
CONTRACTOR_PROMPTS = {
        Contractor.phone.state: ("📱 Введите номер телефона", BackButtons.back_to_welcoming_screen),
        Contractor.tin.state: ("🧾 Введите ИНН", BackButtons.back_to_contractor_phone)        
}

STATE_CONTRACTOR_MAP = {
    "phone": Contractor.phone,
    "tin_number": Contractor.tin
}