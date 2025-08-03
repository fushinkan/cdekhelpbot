from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.utils.state import StateUtils
from bot.states.customer import Customer
from bot.keyboards.backbuttons import BackButtons


router = Router()


@router.message(Customer.city)
async def customer_city_handler(message: Message, state: FSMContext):
    """
    Обработчик города для контрагента.

    Args:
        message (Message): Входящее сообщение с названием города от пользователя.
        state (FSMContext): Контейнер для хранения и управления состоянием контрагента в процессе заполнения формы.
    """
    
    data = await StateUtils.prepare_next_state(obj=message, state=state)
    
    city = message.text.title()
    
    await state.update_data(city=city)
    
    if await StateUtils.edit_invoice_or_data(data=data, message=message, state=state):
        return    
    
    data = await StateUtils.prepare_next_state(obj=message, state=state)
    
    await StateUtils.push_state_to_history(state=state, new_state=Customer.contract_number)
    await state.set_state(Customer.contract_number)
    sent = await message.answer("📄 Введите номер договора (например, KU-ABC7-123)", reply_markup=await BackButtons.back_to_customer_city())
    
    await state.update_data(last_bot_message=sent.message_id)