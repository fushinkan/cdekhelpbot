from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.api.utils.normalize import Normalize
from bot.utils.state import StateUtils

from bot.utils.exceptions import IncorrectPhoneException
from bot.states.customer import Customer


router = Router()
    
    
@router.message(Customer.number)
async def customer_number_handler(message: Message, state: FSMContext):
    """
    Обрабатывает номер(а) телефонов для контрагента.

    Args:
        message (Message): Входящее сообщение с названием города от пользователя.
        state (FSMContext): Контейнер для хранения и управления состоянием контрагента в процессе заполнения формы.
    """
    
    data = await StateUtils.prepare_next_state(obj=message, state=state)
    
    phones = [num.strip() for num in message.text.split(",") if num.strip()]
    normalized_phones = []
    
    try:
        for phone in phones:
            normalized = await Normalize.normalize_phone(phone=phone)
            normalized_phones.append(normalized)
    
    except IncorrectPhoneException as e:
        data = await StateUtils.prepare_next_state(obj=message, state=state)
        sent = await message.answer(str(e))
        
        await state.update_data(error_message=sent.message_id)
        return
    
    await state.update_data(phone=", ".join(normalized_phones))
    data = await StateUtils.prepare_next_state(obj=message, state=state)
    
    if await StateUtils.edit_invoice_or_data(data=data, message=message, state=state):
        return

    await StateUtils.show_customer_summary(data=data, message=message)