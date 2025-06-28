import asyncio

from aiogram.fsm.context import FSMContext
from aiogram import F, Router
from aiogram.types import Message

from bot.utils.delete_messages import delete_prev_messages
from bot.states.invoice import InvoiceForm

from bot.utils.invoice import StateUtils



router = Router()
    
    
@router.message(InvoiceForm.confirmation)
async def confirmation(message: Message, state: FSMContext):
    """
    Обработчик для подтверждения или изменения сводки.
    """
               
    data = await state.get_data()
    last_bot_message_id = data.get("last_bot_message")


    await asyncio.sleep(0.3)
    await message.delete()
    await delete_prev_messages(message, last_bot_message_id) 
    
    
    sent = await StateUtils.get_summary(message, data)
    await state.update_data(last_bot_message=sent.message_id)