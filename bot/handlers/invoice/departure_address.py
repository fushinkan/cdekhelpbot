from aiogram.fsm.context import FSMContext
from aiogram import Router
from aiogram.types import Message


from bot.states.invoice import InvoiceForm
from bot.keyboards.backbuttons import BackButtons
from bot.utils.state import StateUtils


router = Router()


@router.message(InvoiceForm.departure_address)
async def get_departure_address(message: Message, state: FSMContext):
    """
    Обрабатывает ввод адреса отправления в рамках формы InvoiceForm.

    Args:
        message (Message): Входящее сообщение с адресом отправления от пользователя.
        state (FSMContext): Контейнер для хранения и управления состоянием пользователя в процессе заполнения формы.
    """

    data = await StateUtils.prepare_next_state(obj=message, state=state)
    
    departure_address = message.text.strip().title()
    await state.update_data(departure_address=departure_address)
    
    if await StateUtils.edit_invoice_or_data(data=data, message=message, state=state):
        return
    
    await state.set_state(InvoiceForm.recipient_phone)
    await StateUtils.push_state_to_history(state=state, new_state=InvoiceForm.recipient_phone)
    
    sent = await message.answer("📱 Введите номер телефона получателя", reply_markup=await BackButtons.back_to_departure_address())
    
    await state.update_data(last_bot_message=sent.message_id)
