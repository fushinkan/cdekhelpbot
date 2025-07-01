from aiogram.fsm.context import FSMContext
from aiogram import F, Router
from aiogram.types import Message

from bot.states.invoice import InvoiceForm
from bot.keyboards.backbuttons import BackButtons
from bot.utils.invoice import StateUtils
from bot.utils.bot_utils import BotUtils

router = Router()


@router.message(InvoiceForm.departure_city)
async def get_departure_city(message: Message, state: FSMContext):
    """
    Обработчик для получения города отправления.
    """
    data = await StateUtils.prepare_next_state(message, state)
    departure_city = message.text.strip()   
    await state.update_data(departure_city=departure_city)


    if await StateUtils.edit_invoice(data, message, state):
        return
    
    
    await state.set_state(InvoiceForm.departure_address)
    await StateUtils.push_state_to_history(state, InvoiceForm.departure_address)
    
    
    sent = await message.answer("📍 Отлично! Теперь введите адрес отправления/забора груза 🏠", reply_markup=await BackButtons.back_to_departure_city())
    
    
    await state.update_data(last_bot_message=sent.message_id)
