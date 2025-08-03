from aiogram.fsm.context import FSMContext
from aiogram import Router
from aiogram.types import Message

from app.api.utils.normalize import Normalize
from bot.utils.exceptions import IncorrectPhoneException
from bot.states.invoice import InvoiceForm
from bot.keyboards.backbuttons import BackButtons
from bot.utils.state import StateUtils
from bot.utils.bot_utils import BotUtils


router = Router()


@router.message(InvoiceForm.recipient_phone)
async def get_recipient_phone(message: Message, state: FSMContext):
    """
    Обрабатывает ввод номера телефона получателя в рамках формы InvoiceForm.

    Args:
        message (Message): Входящее сообщение с номером телефона получателя от пользователя.
        state (FSMContext): Контейнер для хранения и управления состоянием пользователя в процессе заполнения формы.
    """
        
    data = await StateUtils.prepare_next_state(obj=message, state=state)
    recipient_phone_raw = message.text.strip()

    try:
        recipient_phone = await Normalize.normalize_phone(phone=recipient_phone_raw)
        data = await StateUtils.prepare_next_state(obj=message, state=state)
        
    except IncorrectPhoneException as e:
        data = await StateUtils.prepare_next_state(obj=message, state=state)
        sent = await message.answer(str(e), parse_mode="HTML")
        await state.update_data(error_message=sent.message_id)

        return 
    
    await state.update_data(recipient_phone=recipient_phone)

    if await StateUtils.edit_invoice_or_data(data=data, message=message, state=state):
        return

    await state.set_state(InvoiceForm.recipient_city)
    await StateUtils.push_state_to_history(state=state, new_state=InvoiceForm.recipient_city)
        
    sent = await message.answer("🌆 Пожалуйста, укажите город получателя для доставки", reply_markup=await BackButtons.back_to_recipient_phone())
        
    await state.update_data(last_bot_message=sent.message_id)
        