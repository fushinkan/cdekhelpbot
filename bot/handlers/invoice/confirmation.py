from aiogram.fsm.context import FSMContext
from aiogram import Router
from aiogram.types import Message

from bot.states.invoice import InvoiceForm
from bot.utils.invoice import StateUtils


router = Router()
    
    
@router.message(InvoiceForm.confirmation)
async def confirmation(message: Message, state: FSMContext):
    """
    Обрабатывает ввод пользователя для подтверждения или изменения сводки заказа.

    Args:
        message (Message): Входящее сообщение с ответом пользователя (подтверждение или запрос изменения).
        state (FSMContext): Контейнер для хранения и управления состоянием пользователя в процессе оформления заказа.
    """
           
    data = await StateUtils.prepare_next_state(message, state)    
    
    sent = await StateUtils.get_summary(message, data)
    
    await state.update_data(last_bot_message=sent.message_id)