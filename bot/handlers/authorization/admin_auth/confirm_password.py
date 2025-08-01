import httpx
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.api.utils.validator import Validator
from app.core.config import settings
from bot.keyboards.backbuttons import BackButtons
from bot.states.admin_auth import AdminAuth
from bot.handlers.authorization.main_menu import proceed_to_main_menu
from bot.utils.state import StateUtils
from bot.utils.bot_utils import BotUtils
from bot.utils.exceptions import RequestErrorException, InvalidPasswordException


router = Router()


@router.message(AdminAuth.confirm_password)
async def confirm_password(message: Message, state: FSMContext):
    """
    Подтверждает установку нового пароля для пользователя и записывает его в БД.

    Args:
        message (Message): Объект входящего Telegram-сообщения от пользователя.
        state (FSMContext): Контейнер для хранения и управления текущим состоянием пользователя в рамках авторизации.
    """
    
    data = await StateUtils.prepare_next_state(obj=message, state=state)
    user_id = data.get("id")
    telegram_id = message.from_user.id
    first_password = data.get('new_password')
    confirm_password = message.text.strip()
    
    if confirm_password != first_password:
        data = await BotUtils.delete_error_messages(obj=message, state=state)
        sent = await message.answer("Пароли не совпадают, попробуйте заново", reply_markup=await BackButtons.back_to_phone())
        
        await state.update_data(error_message=sent.message_id)
        await state.set_state(AdminAuth.set_password)
        
        return
   
    if not Validator.validate_password(plain_password=confirm_password):
        data = await BotUtils.delete_error_messages(obj=message, state=state)
        
        sent = await message.answer(
            str(InvalidPasswordException(InvalidPasswordException.__doc__)),
            reply_markup=await BackButtons.back_to_phone()
        )
        
        await state.update_data(error_message=sent.message_id)
        await state.set_state(AdminAuth.set_password)
        
        return  
    
    # Запрос в БД через эндпоинт в API
    async with httpx.AsyncClient() as client:
        try:
            response = await client.put(
                f"{settings.BASE_FASTAPI_URL}/auth/confirm_password",
                json={
                    "telegram_id": telegram_id,
                    "plain_password": first_password,
                    "confirm_password": confirm_password
                }
            )
            
            response.raise_for_status()

            response_user = await client.get(f"{settings.BASE_FASTAPI_URL}/auth/users/{user_id}")
            response_user.raise_for_status()
            user_data = response_user.json()
            
            role = user_data.get("role")
            telegram_id = message.from_user.id
            telegram_name = message.from_user.full_name

            await client.put(
                f"{settings.BASE_FASTAPI_URL}/auth/{role}/{user_id}/login_status",
                json={
                    "is_logged": True,
                    "telegram_id": telegram_id,
                    "telegram_name": telegram_name
                }
            )
            
        except httpx.HTTPStatusError:
            data = await BotUtils.delete_error_messages(obj=message, state=state)
            sent = await message.answer(
                "❌ Ошибка при подтверждении пароля. Попробуйте заново",
                reply_markup=await BackButtons.back_to_welcoming_screen()
            )
            
            await state.update_data(error_message=sent.message_id)
            return
        
        except httpx.RequestError:
            data = await BotUtils.delete_error_messages(obj=message, state=state)
            sent = await message.answer(
                str(RequestErrorException(RequestErrorException.__doc__)),
                reply_markup=await BackButtons.back_to_welcoming_screen()
            )
            
            await state.update_data(error_message=sent.message_id)
            return       
        
        data = await BotUtils.delete_error_messages(obj=message, state=state)
                
        await proceed_to_main_menu(role=user_data.get("role"), user_data=user_data, message=message)
        await state.clear()
 