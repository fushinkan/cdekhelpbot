from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.api.utils.security import Security
from app.core.config import settings
from bot.keyboards.backbuttons import BackButtons
from bot.states.admin_auth import AdminAuth
from bot.handlers.authorization.main_menu import proceed_to_main_menu
from bot.utils.state import StateUtils
from bot.utils.exceptions import RequestErrorException, InvalidTokenException
from bot.utils.storage import Welcome
from bot.keyboards.basic import BasicKeyboards

import httpx
import asyncio


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
    telegram_name = message.from_user.username
    first_password = data.get('new_password')
    second_psw = message.text.strip()
    is_change = data.get("is_change", False)
    
    if first_password != second_psw:
        data = await StateUtils.prepare_next_state(obj=message, state=state)
        if not is_change:
            sent = await message.answer("Пароли не совпадают, попробуйте заново", reply_markup=await BackButtons.back_to_phone())
            await state.update_data(error_message=sent.message_id)
            await state.set_state(AdminAuth.set_password)
            return

        else:
            sent = await message.answer("Пароли не совпадают, попробуйте заново", reply_markup=await BackButtons.back_to_settings())
            await state.update_data(error_message=sent.message_id)
            await state.set_state(AdminAuth.set_password)
            return  

    # Запрос в БД через эндпоинт в API
    async with httpx.AsyncClient() as client:
        try:
            response = await client.put(
                f"{settings.BASE_FASTAPI_URL}/auth/confirm_password",
                json={
                    "user_id": user_id,
                    "confirm_password": second_psw,
                    "is_change": is_change,
                    "telegram_id": telegram_id,
                    "telegram_name": telegram_name
                }
            )
            
            response.raise_for_status()
            response_data = response.json()
            access_token = response_data.get("access_token")
            if not access_token:
                sent = await message.answer(str(InvalidTokenException(InvalidTokenException.__doc__)))
                await asyncio.sleep(5)
                await sent.delete()
                return
            
            user_data = await Security.decode_jwt(access_token=access_token)
         
        except httpx.HTTPStatusError:
            data = await StateUtils.prepare_next_state(obj=message, state=state)
            sent = await message.answer(
                "❌ Ошибка при подтверждении пароля. Попробуйте заново",
                reply_markup=await BackButtons.back_to_welcoming_screen()
            )
            
            await state.update_data(error_message=sent.message_id)
            return
        
        except httpx.RequestError:
            data = await StateUtils.prepare_next_state(obj=message, state=state)
            sent = await message.answer(
                str(RequestErrorException(RequestErrorException.__doc__)),
                reply_markup=await BackButtons.back_to_welcoming_screen()
            )
            
            await state.update_data(error_message=sent.message_id)
            return       
        
        data = await StateUtils.prepare_next_state(obj=message, state=state)
            
        if not is_change:   
            await proceed_to_main_menu(user_data=user_data, message=message, state=state)
            await state.update_data(user_data=user_data, access_token=access_token)
            
        else:
            await message.answer(Welcome.WELCOME, reply_markup=await BasicKeyboards.get_welcoming_kb())
            await state.update_data(user_data=user_data, access_token=access_token)