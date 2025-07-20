from aiogram.fsm.context import FSMContext
from aiogram import Router
from aiogram.types import Message

from bot.states.invoice import InvoiceForm
from bot.keyboards.backbuttons import BackButtons
from bot.utils.invoice import StateUtils


router = Router()


@router.message(InvoiceForm.departure_city)
async def get_departure_city(message: Message, state: FSMContext):
    """
    Обрабатывает ввод города отправления в рамках формы InvoiceForm.

    Args:
        message (Message): Входящее сообщение с названием города от пользователя.
        state (FSMContext): Контейнер для хранения и управления состоянием пользователя в процессе заполнения формы.
    """
    
    data = await StateUtils.prepare_next_state(obj=message, state=state)
    departure_city = message.text.strip()   
    await state.update_data(departure_city=departure_city)

    if await StateUtils.edit_invoice(data=data, message=message, state=state):
        return
    
    await state.set_state(InvoiceForm.departure_address)
    await StateUtils.push_state_to_history(state=state, new_state=InvoiceForm.departure_address)
    
    sent = await message.answer("📍 Отлично! Теперь введите адрес отправления/забора груза 🏠", reply_markup=await BackButtons.back_to_departure_city())
    
    await state.update_data(last_bot_message=sent.message_id)
