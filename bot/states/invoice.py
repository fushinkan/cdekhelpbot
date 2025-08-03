from aiogram.fsm.state import State, StatesGroup

from bot.keyboards.customer import CustomerKeyboards
from bot.keyboards.backbuttons import BackButtons


class InvoiceForm(StatesGroup):
    """
    Состояния для поэтапного создания накладной в Telegram-боте.

    Атрибуты:
        cmd_start (State): Состояние для сброса введенных данных.
        contract_number (State): Ввод номера договора.
        departure_city (State): Ввод города отправления.
        departure_address (State): Ввод адреса отправления.
        recipient_phone (State): Ввод телефона получателя.
        recipient_city (State): Ввод города получателя.
        recipient_address (State): Ввод адреса получателя.
        insurance_amount (State): Ввод суммы страхования.
        confirmation (State): Подтверждение или изменение сводки.
        editing_field (State): Выбор поля для редактирования.
    """
    cmd_start = State()
    contract_number = State()
    departure_city = State()
    departure_address = State()
    recipient_phone = State()
    recipient_city = State()
    recipient_address = State()
    insurance_amount = State()
    confirmation = State()
    editing_field = State()
    
    
INVOICE_STATE = {
    InvoiceForm.contract_number,
    InvoiceForm.departure_city,
    InvoiceForm.departure_address,
    InvoiceForm.recipient_phone,
    InvoiceForm.recipient_city,
    InvoiceForm.recipient_address,
}


INVOICE_PROMPTS = {
    InvoiceForm.departure_city.state: ("🏙 Пожалуйста, введите город отправления", BackButtons.back_to_menu),
    InvoiceForm.departure_address.state: ("📍 Введите адрес отправления/забора груза 🏠", BackButtons.back_to_departure_city),
    InvoiceForm.recipient_phone.state: ("📱 Введите номер телефона получателя", BackButtons.back_to_departure_address),
    InvoiceForm.recipient_city.state: ("🌆 Пожалуйста, укажите город получателя для доставки", BackButtons.back_to_recipient_phone),
    InvoiceForm.recipient_address.state: ("📍 Укажите адрес получения/доставки", BackButtons.back_to_recipient_city),
    InvoiceForm.insurance_amount.state: ("🛡️ На какую сумму нужна страховка?", BackButtons.back_to_recipient_address),
    InvoiceForm.confirmation.state: ("🛠️ Добавить доп. услуги к заказу?", CustomerKeyboards.extra_services), 
}


STATE_MAP = {
    "departure_city": InvoiceForm.departure_city,
    "departure_address": InvoiceForm.departure_address,
    "recipient_phone": InvoiceForm.recipient_phone,
    "recipient_city": InvoiceForm.recipient_city,
    "recipient_address": InvoiceForm.recipient_address,
    "insurance_amount": InvoiceForm.insurance_amount,
}