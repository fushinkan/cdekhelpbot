from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram import Router
from aiogram.types import Message

from app.api.handlers.normalize import normalize_phone

from bot.utils.exceptions import IncorrectPhone
from bot.states.invoice import InvoiceForm
from bot.keyboards.backbuttons import BackButtons
from bot.utils.invoice import StateUtils
from bot.utils.bot_utils import BotUtils

router = Router()


@router.message(InvoiceForm.recipient_phone)
async def get_recipient_phone(message: Message, state: FSMContext):
    """
    Обработчик для получения номера телефона получателя.
    """
        
    data = await StateUtils.prepare_next_state(message, state)


    recipient_phone_raw = message.text.strip()


    try:
        recipient_phone = await normalize_phone(recipient_phone_raw)
    except IncorrectPhone as e:
        sent = await message.answer(str(e), parse_mode="HTML")
        await state.update_data(error_message=sent.message_id)
        return 
    
    await state.update_data(recipient_phone=recipient_phone)

    if await StateUtils.edit_invoice(data, message, state):
        return

    data = await state.get_data()
    error_message = data.get("error_message")
    try:
        if error_message:
            await BotUtils.delete_prev_messages(message, error_message)      
    except TelegramBadRequest:
        pass

    await state.set_state(InvoiceForm.recipient_city)
    await StateUtils.push_state_to_history(state, InvoiceForm.recipient_city)
        
        
    sent = await message.answer("🌆 Пожалуйста, укажите город получателя для доставки", reply_markup=await BackButtons.back_to_recipient_phone())

        
    await state.update_data(last_bot_message=sent.message_id)
        