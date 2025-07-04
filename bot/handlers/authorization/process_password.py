import asyncio
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram import F, Router
from aiogram.types import Message

from app.api.utils.security import verify_password
from app.db.base import async_session_factory
from app.api.handlers.get_user import UserInDB
from bot.utils.exceptions import IncorrectPasswordException
from bot.keyboards.admin import AdminKeyboards
from bot.utils.bot_utils import BotUtils
from bot.states.admin_auth import AdminAuth
from bot.utils.exceptions import UserNotExistsException

router = Router()


@router.message(AdminAuth.password)
async def process_password(message: Message, state: FSMContext):
    """
    Проверяет корректность введенного пароля.
    """
    
    await asyncio.sleep(0.2)
    
    
    data = await state.get_data()
    last_bot_message_id = data.get("last_bot_message")
    role = data.get("role")
    phone = data.get("phone")
    
    async with async_session_factory() as session:
        if role == "admin":
            user = await UserInDB.get_admin_by_phone(phone_number=phone, session=session)
        elif role == "user":
            user = await UserInDB.get_client_by_phone(phone_number=phone, session=session)
        else:
            user = None
    
    
    if role is None and phone is None and user is None:
        sent = await message.answer(UserNotExistsException(UserNotExistsException.__doc__))
        await asyncio.sleep(3)
        await message.delete()
        await sent.delete()
        await state.clear()
        return
    
    
    entered_password = message.text.strip()
    
       
    await BotUtils.delete_prev_messages(obj=message, message_id=last_bot_message_id)
        
    try:   
        if verify_password(entered_password, user.hashed_psw):
            sent = await message.answer((
            f"👋 Здравствуйте, {user.contractor}\n\n"
            "Добро пожаловать в панель управления.\n"
            "Здесь вы можете управлять пользователями и контролировать систему.\n"
            "Выберите нужный пункт меню, чтобы начать работу."
        ), reply_markup=await AdminKeyboards.get_admin_kb())
        await message.delete()
            
    except IncorrectPasswordException as e:
        sent = await message.answer(str(e), parse_mode="HTML")
        await state.update_data(error_message=sent.message_id)
        return 
    
    
    data = await state.get_data()
    error_message = data.get("error_message")
    try:
        if error_message:
            await BotUtils.delete_prev_messages(message, error_message)      
    except TelegramBadRequest:
        pass
    
    
    await state.clear()
    
 