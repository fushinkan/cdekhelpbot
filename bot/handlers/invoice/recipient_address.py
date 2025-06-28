import asyncio

from aiogram.fsm.context import FSMContext
from aiogram import F, Router
from aiogram.types import Message


from bot.utils.delete_messages import delete_prev_messages
from bot.states.invoice import InvoiceForm
from bot.keyboards.backbuttons import BackButtons
from bot.utils.invoice import StateUtils


router = Router()
    
    
@router.message(InvoiceForm.recipient_address)
async def get_recipient_address(message: Message, state: FSMContext):
    """
    Обработчик для получения адреса доставки.
    """
        
    data = await state.get_data()
    last_bot_message_id = data.get("last_bot_message")
    recipient_address = message.text.strip()


    await asyncio.sleep(0.3)
    await message.delete()
    await delete_prev_messages(message, last_bot_message_id) 
    
    
    await state.update_data(recipient_address=recipient_address)
    await state.set_state(InvoiceForm.insurance_amount)
    await StateUtils.push_state_to_history(state, InvoiceForm.insurance_amount)
    
    sent = await message.answer("🛡️ На какую сумму нужна страховка?", reply_markup=await BackButtons.back_to_recipient_address())
    
    
    await state.update_data(last_bot_message=sent.message_id)
    
