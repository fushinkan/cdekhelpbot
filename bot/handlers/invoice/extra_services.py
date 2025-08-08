from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.states.invoice import InvoiceForm
from bot.utils.state import StateUtils


router = Router()


@router.message(InvoiceForm.extra_services)
async def input_extra_services(message: Message, state: FSMContext):
    """
    Обрабатывает ввод дополнительных услуг пользователем.

    Args:
        message (Message): Входящее сообщение с номером телефона получателя от пользователя.
        state (FSMContext): Контейнер для хранения и управления состоянием пользователя в процессе заполнения формы.
    """
        
    extra_services = message.text.capitalize()
    await state.update_data(extra=extra_services)

    
    data = await StateUtils.prepare_next_state(obj=message, state=state)
    
    if await StateUtils.edit_invoice_or_data(data=data, message=message, state=state):
        return
    
    #await state.set_state(InvoiceForm.confirmation)
    #await StateUtils.push_state_to_history(state=state, new_state=InvoiceForm.confirmation)
    
    sent = await StateUtils.send_summary(data=data, message=message, for_admin=False)
    
    await state.update_data(last_bot_message=sent.message_id)
