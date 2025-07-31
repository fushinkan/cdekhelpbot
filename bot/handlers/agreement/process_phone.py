from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.api.utils.normalize import normalize_phone
from bot.states.contractor import Contractor
from bot.utils.state import StateUtils
from bot.utils.bot_utils import BotUtils
from bot.utils.exceptions import IncorrectPhoneException
from bot.keyboards.backbuttons import BackButtons


router = Router()


@router.message(Contractor.phone)
async def process_tin_contractor(message: Message, state: FSMContext):
    """
    Обрабатывает ввод номера телефона пользователя в рамках формы Contractor.

    Args:
        message (Message): Входящее сообщение с номером телефона от пользователя.
        state (FSMContext): Контейнер для хранения и управления состоянием пользователя в процессе заполнения формы.
    """
    
    data = await StateUtils.prepare_next_state(obj=message, state=state)
    
    try:
        phone = await normalize_phone(phone=message.text.strip())
        data = await BotUtils.delete_error_messages(obj=message, state=state)
        
        await state.update_data(phone=phone)
        
        if await StateUtils.edit_invoice_or_data(data=data, message=message, state=state):
            return
        
    except IncorrectPhoneException as e:
        data = await BotUtils.delete_error_messages(obj=message, state=state)
        sent = await message.answer(str(e), parse_mode="HTML")
        
        await state.update_data(error_message=sent.message_id)
        
        return
    
    await state.update_data(phone=phone)
    
    sent = await message.answer("🧾 Введите ИНН", reply_markup=await BackButtons.back_to_contractor_phone())
    await state.update_data(last_bot_message=sent.message_id)
    await state.set_state(Contractor.tin)