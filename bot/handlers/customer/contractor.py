from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.utils.state import StateUtils
from bot.states.customer import Customer
from bot.keyboards.backbuttons import BackButtons


router = Router()


@router.message(Customer.contractor)
async def contractor_handler(message: Message, state: FSMContext):
    """
    Обработчик наименования для контрагента.

    Args:
        message (Message): Входящее сообщение с названием города от пользователя.
        state (FSMContext): Контейнер для хранения и управления состоянием контрагента в процессе заполнения формы.
    """
    contractor = message.text.title()
    
    await state.update_data(contractor=contractor)
    
    data = await StateUtils.prepare_next_state(obj=message, state=state)
    
    if await StateUtils.edit_invoice_or_data(data=data, message=message, state=state):
        return
    
    await StateUtils.push_state_to_history(state=state, new_state=Customer.city)
    await state.set_state(Customer.city)
    
    sent = await message.answer("🏙 Введите город контрагента", reply_markup=await BackButtons.back_to_customer_contractor())
    await state.update_data(last_bot_message=sent.message_id)