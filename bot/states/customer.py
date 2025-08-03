from aiogram.fsm.state import State, StatesGroup

from bot.keyboards.backbuttons import BackButtons

class Customer(StatesGroup):
    """
    Состояния для поэтапного доавбления информации о новом контрагенте.
    
    Args:
        contractor (State): Наименование контрагента.
        city (State): Город контрагента.
        contract_number (State): Номер договора контрагента.
        number (State): Номера телефонов контрагента.
    """
    
    contractor = State()
    city = State()
    contract_number = State()
    number = State()


CUSTOMER_STATE = {
    Customer.contractor,
    Customer.contract_number,
    Customer.city.state,
    Customer.number,
}


    
CUSTOMER_PROMPTS = {
        Customer.contractor.state: ("👤 Введите имя контрагента", BackButtons.back_to_customer_contractor),
        Customer.city.state: ("🏙 Введите город контрагента", BackButtons.back_to_customer_city),
        Customer.contract_number.state: ("📄 Введите номер договора (например, KU-ABC7-123)", BackButtons.back_to_customer_contract_number),
        Customer.number.state: ("📱 Введите номера телефонов через запятую (например, 89042803001, 89991234567)", BackButtons.back_to_customer_number), 
}


CUSTOMER_STATE_MAP = {
    "contractor": Customer.contractor,
    "contract_number": Customer.contract_number,
    "city": Customer.city.state,
    "number": Customer.number,
}