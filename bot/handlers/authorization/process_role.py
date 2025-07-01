import asyncio

from aiogram.fsm.context import FSMContext
from aiogram import F, Router
from aiogram.types import Message

from app.api.handlers.normalize import normalize_phone
from bot.utils.exceptions import UserNotExistsException, IncorrectPhone
from bot.keyboards.customer import CustomerKeyboards
from bot.keyboards.backbuttons import BackButtons
from bot.utils.fetch_user import fetch_user_by_phone
from bot.utils.bot_utils import BotUtils
from bot.states.admin import AdminAuth

router = Router()


@router.message(AdminAuth.waiting_for_phone)
async def process_role(message: Message, state: FSMContext):
    """
    Проверяет роль пользователя.
    
    Если роль админ, то запрашивает его пароль.
    """
    
    await asyncio.sleep(0.2)
    
    
    data = await state.get_data()
    last_bot_message_id = data.get("last_bot_message")
    
    
    try:
        phone = await normalize_phone(message.text)
        user = await fetch_user_by_phone(phone)     
        await BotUtils.delete_prev_messages(message, message_id=last_bot_message_id)
        await message.delete()
        
    except (IncorrectPhone, UserNotExistsException) as e:
        sent = await message.answer(str(e), parse_mode="HTML")
        await asyncio.sleep(2)
        await message.delete()
        await sent.delete()
        return
    
    
    await state.update_data(phone=phone)
    
    
    if user.role == "admin":
        sent = await message.answer("Пожалуйста, введите ваш пароль для подтверждения доступа.", reply_markup=await BackButtons.back_to_phone())
        await state.set_state(AdminAuth.waiting_for_password)
        await state.update_data(last_bot_message=sent.message_id)
        await asyncio.sleep(2)
    else:
        sent = await message.answer("Вы успешно вошли! Рекомендуется установить пароль для безопасности.", reply_markup=await CustomerKeyboards.password_kb())
        await state.update_data(last_bot_message=sent.message_id)
        await asyncio.sleep(2)