from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram import Router

from app.core.config import settings
from bot.states.merch import Merch
from bot.utils.validate import Validator
from bot.utils.exceptions import IncorrectTinNumberException
from bot.utils.state import StateUtils
from bot.utils.storage import CustomerText

import asyncio


router = Router()


@router.message(Merch.tin)
async def receive_tin(message: Message, state: FSMContext):
    """
    Валидирует ИНН и отправляет в чат с менеджерами

    Args:
        message (Message): Входящее сообщение с ИНН от пользователя.
        state (FSMContext): Контейнер для хранения и управления состоянием пользователя в процессе заполнения формы.
    """
    
    tin = message.text.strip()
    data = await StateUtils.prepare_next_state(obj=message, state=state)

    try:
        await Validator.correct_tin_number(text=tin)
        text = CustomerText.MERCH_REQUEST_TEXT.format(
            tin=tin,
            username=message.from_user.username or "-"
        )

    except IncorrectTinNumberException as e:
        data = await StateUtils.prepare_next_state(obj=message, state=state)
        sent = await message.answer(str(e), parse_mode="HTML")
        await state.update_data(error_message=sent.message_id)
        return

    await state.update_data(tin_number=tin)
    
    chat_id = settings.INVOICE_CHAT_ID
    await message.bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML")
    

    sent = await message.answer(
        "✅ Спасибо! Ваша заявка принята. Мы свяжемся с вами в течение 24 часов."
    )
    
    await asyncio.sleep(5)
    await sent.delete()
    await state.clear() 