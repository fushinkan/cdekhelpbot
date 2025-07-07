from aiogram.fsm.context import FSMContext
from aiogram import Router
from aiogram.types import Message

from bot.states.invoice import InvoiceForm
from bot.keyboards.backbuttons import BackButtons
from bot.utils.invoice import StateUtils


router = Router()
    

@router.message(InvoiceForm.recipient_city)
async def get_recipient_city(message: Message, state: FSMContext):
    """
    Обработчик для поулчения города получателя.
    """
    
    data = await StateUtils.prepare_next_state(message, state)


    recipient_city = message.text.strip()
    await state.update_data(recipient_city=recipient_city)
    
    
    if await StateUtils.edit_invoice(data, message, state):
        return
    
    
    await state.set_state(InvoiceForm.recipient_address)
    await StateUtils.push_state_to_history(state, InvoiceForm.recipient_address)
    
    
    sent = await message.answer("📍 Отлично! Теперь укажите адрес получения/доставки", reply_markup=await BackButtons.back_to_recipient_city())
    
    
    await state.update_data(last_bot_message=sent.message_id)
    