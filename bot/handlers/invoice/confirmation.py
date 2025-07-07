import asyncio

from aiogram.fsm.context import FSMContext
from aiogram import Router
from aiogram.types import Message
from bot.states.invoice import InvoiceForm

from bot.utils.invoice import StateUtils


router = Router()
    
    
@router.message(InvoiceForm.confirmation)
async def confirmation(message: Message, state: FSMContext):
    """
    Обработчик для подтверждения или изменения сводки.
    """
           
    data = await StateUtils.prepare_next_state(message, state)    
    
    
    sent = await StateUtils.get_summary(message, data)
    
    
    await state.update_data(last_bot_message=sent.message_id)