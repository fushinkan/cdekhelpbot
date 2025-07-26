from aiogram.fsm.state import State, StatesGroup

class SendInvoice(StatesGroup):
    """
    Состояние для передачи информации о пользователе для предоставления накладной. 

    Наследуется от:
        StatesGroup: Базовый класс для описания состояний в FSM.
        
    Атрибуты:
        waiting_for_invoice (State): Состояние в которое сохраняется информация пользователя.
    """
    
    waiting_for_invoice = State()