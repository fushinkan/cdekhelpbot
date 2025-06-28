import asyncio

from aiogram.fsm.context import FSMContext
from aiogram import F, Router
from aiogram.types import Message

from bot.utils.validate import InvoiceValidator
from bot.utils.exceptions import IncorrectPhone
from bot.utils.delete_messages import delete_prev_messages
from bot.states.invoice import InvoiceForm
from bot.keyboards.backbuttons import BackButtons
from bot.utils.invoice import StateUtils


router = Router()


@router.message(InvoiceForm.recipient_phone)
async def get_recipient_phone(message: Message, state: FSMContext):
    """
    Обработчик для получения номера телефона получателя.
    """
    
    data = await state.get_data()
    last_bot_message_id = data.get("last_bot_message")
    recipient_phone = message.text.strip()

    try:
        await InvoiceValidator.correct_phone(recipient_phone)
    except IncorrectPhone as e:
        sent = await message.answer(str(e), parse_mode="HTML")
        await asyncio.sleep(5)
        await message.delete()
        await sent.delete()
        return 
    
    
    await asyncio.sleep(1)
    await message.delete()
    await delete_prev_messages(message, last_bot_message_id)   
    
    
    await state.update_data(recipient_phone=recipient_phone)
    await state.set_state(InvoiceForm.recipient_city)
    await StateUtils.push_state_to_history(state, InvoiceForm.recipient_city)
    
    
    sent = await message.answer("🌆 Пожалуйста, укажите город получателя для доставки", reply_markup=await BackButtons.back_to_recipient_phone())

    
    await state.update_data(last_bot_message=sent.message_id)
    