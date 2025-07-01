from aiogram.fsm.context import FSMContext
from aiogram import F, Router
from aiogram.types import Message

from bot.states.invoice import InvoiceForm
from bot.keyboards.backbuttons import BackButtons
from bot.utils.invoice import StateUtils
from bot.utils.delete_messages import delete_prev_messages

router = Router()
    

@router.message(InvoiceForm.recipient_city)
async def get_recipient_city(message: Message, state: FSMContext):
    """
    Обработчик для поулчения города получателя.
    """
    
    data = await StateUtils.prepare_next_state(message, state)


    recipient_city = message.text.strip()
    await state.update_data(recipient_city=recipient_city)
    
    
    if data.get("editing_field"):
        await state.update_data(editing_field=None)
        updated_data = await state.get_data()
        updated_summary = await StateUtils.get_summary(message, updated_data)
        await state.update_data(last_bot_message_id=updated_summary.message_id)
        await delete_prev_messages(message, updated_data.get("last_bot_message_id"))
        return
    
    
    await state.set_state(InvoiceForm.recipient_address)
    await StateUtils.push_state_to_history(state, InvoiceForm.recipient_address)
    
    
    sent = await message.answer("📍 Отлично! Теперь укажите адрес получения/доставки", reply_markup=await BackButtons.back_to_recipient_city())
    
    
    await state.update_data(last_bot_message=sent.message_id)
    