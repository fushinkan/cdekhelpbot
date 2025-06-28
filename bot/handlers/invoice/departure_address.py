import asyncio

from aiogram.fsm.context import FSMContext
from aiogram import F, Router
from aiogram.types import Message

from bot.utils.delete_messages import delete_prev_messages
from bot.states.invoice import InvoiceForm
from bot.keyboards.backbuttons import BackButtons
from bot.utils.invoice import StateUtils


router = Router()


@router.message(InvoiceForm.departure_address)
async def get_departure_address(message: Message, state: FSMContext):
    """
    Обработчик для адреса отправления.
    """
    
    data = await state.get_data()
    last_bot_message_id = data.get("last_bot_message")
    departure_address = message.text.strip()
    
    
    await asyncio.sleep(0.3)
    await message.delete()
    await delete_prev_messages(message, last_bot_message_id)
    
    
    await state.update_data(departure_address=departure_address)
    await state.set_state(InvoiceForm.recipient_phone)
    await StateUtils.push_state_to_history(state, InvoiceForm.recipient_phone)
    
    
    sent = await message.answer("📱 Введите номер телефона получателя", reply_markup=await BackButtons.back_to_departure_address())
    
    
    await state.update_data(last_bot_message=sent.message_id)
