from aiogram.fsm.context import FSMContext
from aiogram import Router
from aiogram.types import Message

from bot.states.invoice import InvoiceForm
from bot.keyboards.backbuttons import BackButtons
from bot.utils.state import StateUtils


router = Router()
    

@router.message(InvoiceForm.recipient_city)
async def get_recipient_city(message: Message, state: FSMContext):
    """
    Обрабатывает ввод города получателя в рамках формы InvoiceForm.

    Args:
        message (Message): Входящее сообщение с названием города получателя от пользователя.
        state (FSMContext): Контейнер для хранения и управления состоянием пользователя в процессе заполнения формы.
    """
    
    data = await StateUtils.prepare_next_state(obj=message, state=state)
    recipient_city = message.text.strip().title()
    
    await state.update_data(recipient_city=recipient_city)
    
    if await StateUtils.edit_invoice_or_data(data=data, message=message, state=state):
        return
    
    await state.set_state(InvoiceForm.recipient_address)
    await StateUtils.push_state_to_history(state=state, new_state=InvoiceForm.recipient_address)
    
    sent = await message.answer("📍 Отлично! Теперь укажите адрес получения/доставки", reply_markup=await BackButtons.back_to_recipient_city())
    
    await state.update_data(last_bot_message=sent.message_id)
    