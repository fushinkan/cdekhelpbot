import asyncio
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram import Router
from aiogram.types import Message

from app.api.utils.auth import AuthUtils
from app.db.base import async_session_factory
from bot.utils.exceptions import UserNotExistsException
from bot.utils.exceptions import IncorrectPhone
from bot.utils.exceptions import IncorrectPasswordException
from bot.keyboards.customer import CustomerKeyboards
from bot.keyboards.backbuttons import BackButtons
from bot.utils.bot_utils import BotUtils
from bot.states.admin_auth import AdminAuth
from bot.states.auth import Auth

router = Router()


@router.message(Auth.waiting_for_phone)
async def process_role(message: Message, state: FSMContext):
    """
    Проверяет роль пользователя в базе данных.
    
    Если роль админ, то запрашивает его пароль.
    """
    
    await asyncio.sleep(0.2)
    
    
    data = await state.get_data()
    last_bot_message_id = data.get("last_bot_message")
    await BotUtils.delete_prev_messages(message, last_bot_message_id)
    
    async with async_session_factory() as session:
        try:
            role, obj, phone_number = await AuthUtils.process_role_in_db(phone_number=message.text, session=session)
            
            if phone_number is None:
                raise IncorrectPhone(IncorrectPhone.__doc__)
            
            if obj is None:
                raise UserNotExistsException(UserNotExistsException.__doc__)
            
            
            await BotUtils.delete_prev_messages(message, message_id=last_bot_message_id)
            await message.delete()
            
        except UserNotExistsException as e:
            sent = await message.answer(str(e), parse_mode="HTML")
            await asyncio.sleep(2)
            await message.delete()
            await sent.delete()
            return

        except (IncorrectPhone, IncorrectPasswordException) as e:
            sent = await message.answer(str(e), parse_mode="HTML")
            await state.update_data(error_message=sent.message_id)
            return 
        
        await state.update_data(
            phone=phone_number,
            role=role,
        )
    
    
        data = await state.get_data()
        error_message = data.get("error_message")
        try:
            if error_message:
                await BotUtils.delete_prev_messages(message, error_message)      
        except TelegramBadRequest:
            pass
    
    
    if role == "admin":
        sent = await message.answer("Пожалуйста, введите ваш пароль для подтверждения доступа.", reply_markup=await BackButtons.back_to_phone())
        await state.set_state(AdminAuth.password)
        await state.update_data(last_bot_message=sent.message_id)
        await asyncio.sleep(2)
    else:
        sent = await message.answer("Вы успешно вошли! Рекомендуется установить пароль для безопасности.", reply_markup=await CustomerKeyboards.password_kb())
        await state.update_data(last_bot_message=sent.message_id)
        await asyncio.sleep(2)