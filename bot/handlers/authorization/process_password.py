import asyncio

from aiogram.fsm.context import FSMContext
from aiogram import F, Router
from aiogram.types import Message

from app.api.utils.security import verify_password
from bot.utils.exceptions import IncorrectPasswordException
from bot.keyboards.admin import AdminKeyboards
from bot.utils.fetch_user import fetch_user_by_phone
from bot.utils.bot_utils import BotUtils
from bot.states.admin import AdminAuth

router = Router()


@router.message(AdminAuth.waiting_for_password)
async def process_password(message: Message, state: FSMContext):
    """
    Проверяет корректность введенного пароля.
    """
    
    await asyncio.sleep(0.2)
    
    
    data = await state.get_data()
    last_bot_message_id = data.get("last_bot_message")
    phone = data.get("phone")
    user = await fetch_user_by_phone(phone)
    entered_password = message.text.strip()
    
       
    await BotUtils.delete_prev_messages(message, last_bot_message_id)
        
        
    if not verify_password(entered_password, user.hashed_psw):
        sent = await message.answer(IncorrectPasswordException.__doc__)
        await asyncio.sleep(2)
        await message.delete()
        await sent.delete()
        return
    
    
    await message.delete()
    

    await message.answer((
        f"👋 Здравствуйте, {user.contractor}\n\n"
        "Добро пожаловать в панель управления.\n"
        "Здесь вы можете управлять пользователями и контролировать систему.\n"
        "Выберите нужный пункт меню, чтобы начать работу."
    ), reply_markup=await AdminKeyboards.get_admin_kb())
    
    
    await state.clear()
    
 