from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.api.utils.security import Security
from app.core.config import settings
from bot.keyboards.backbuttons import BackButtons
from bot.states.customer_auth import CustomerAuth
from bot.handlers.authorization.main_menu import proceed_to_main_menu
from bot.utils.state import StateUtils
from bot.utils.exceptions import RequestErrorException, InvalidTokenException
from bot.utils.storage import Welcome
from bot.keyboards.basic import BasicKeyboards

import httpx
import asyncio


router = Router()


@router.message(CustomerAuth.confirm_password)
async def confirm_password(message: Message, state: FSMContext):
    """
    Подтверждает установку нового пароля для пользователя и записывает его в БД.

    Args:
        message (Message): Объект входящего Telegram-сообщения от пользователя.
        state (FSMContext): Контейнер для хранения и управления текущим состоянием пользователя в рамках авторизации.
    """
    
    data = await StateUtils.prepare_next_state(obj=message, state=state)
    telegram_id = message.from_user.id
    telegram_name = message.from_user.username
    user_id = data.get("id")
    first_password = data.get('new_password')
    second_psw = message.text.strip()
    is_change = data.get("is_change", False)
    
    if first_password != second_psw:
        data = await StateUtils.prepare_next_state(obj=message, state=state)
        if not is_change:
            sent = await message.answer("Пароли не совпадают, попробуйте заново", reply_markup=await BackButtons.back_to_phone())
            await state.update_data(error_message=sent.message_id)
            await state.set_state(CustomerAuth.set_password)
            return

        else:
            sent = await message.answer("Пароли не совпадают, попробуйте заново", reply_markup=await BackButtons.back_to_settings())
            await state.update_data(error_message=sent.message_id)
            await state.set_state(CustomerAuth.set_password)
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
            refresh_token = response_data.get("refresh_token")
            if not access_token and not refresh_token:
                sent = await message.answer(str(InvalidTokenException(InvalidTokenException.__doc__)))
                await asyncio.sleep(5)
                await sent.delete()
                return
            
            user_data = await Security.decode_jwt(access_token=access_token)

            await client.post(
                f"{settings.BASE_FASTAPI_URL}/tokens/",
                json={
                    "user_id": user_id,
                    "access_token": access_token,
                    "refresh_token": refresh_token
                }
            )  

        except httpx.HTTPStatusError:
            sent = await message.answer(
                "❌ Ошибка при подтверждении пароля. Попробуйте заново",
                reply_markup=await BackButtons.back_to_welcoming_screen()
            )
            
            await asyncio.sleep(5)
            await sent.delete()
            return
        
        except httpx.RequestError:
            sent = await message.answer(
                str(RequestErrorException(RequestErrorException.__doc__)),
                reply_markup=await BackButtons.back_to_welcoming_screen()
            )
            
            await asyncio.sleep(5)
            await sent.delete()
            return  
            
        if not is_change:
            await proceed_to_main_menu(user_data=user_data, message=message, state=state)
            await state.set_state(CustomerAuth.main_menu)
            await state.update_data(user_data=user_data)
        
        else:
            await message.answer(Welcome.WELCOME, reply_markup=await BasicKeyboards.get_welcoming_kb())
            await state.update_data(user_data=user_data)