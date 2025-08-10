from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.api.utils.security import Security
from app.core.config import settings
from bot.utils.state import StateUtils
from bot.states.admin_auth import AdminAuth
from bot.handlers.authorization.main_menu import proceed_to_main_menu
from bot.keyboards.backbuttons import BackButtons
from bot.utils.exceptions import RequestErrorException, IncorrectPasswordException, InvalidTokenException

import httpx
import asyncio


router = Router()


@router.message(AdminAuth.enter_password)
async def accept_enter(message: Message, state: FSMContext):
    """
    Проверяет правильность введенного пароля и пароля сохраненного в БД.

    Args:
        message (Message): Объект входящего Telegram-сообщения от пользователя.
        state (FSMContext): Контейнер для хранения и управления текущим состоянием пользователя в рамках авторизации.

    Raises:
        UserNotExistsException: Кастомный класс с ошибкой.
        IncorrectPasswordException: Кастомный класс с ошибкой.
    """

    data = await StateUtils.prepare_next_state(obj=message, state=state)
    phone_number = data.get("phone")
    user_id = data.get("id")
    password = message.text.strip()
    telegram_id = message.from_user.id
    telegram_name = message.from_user.username

    data = await StateUtils.prepare_next_state(obj=message, state=state)

    # Запрос в БД через эндпоинт в API
    async with httpx.AsyncClient() as client:
        try:
            
            response = await client.post(
                f"{settings.BASE_FASTAPI_URL}/auth/accept_enter",
                json={
                    "phone_number": phone_number,
                    "user_id": user_id,
                    "password": password,
                    "telegram_id": telegram_id,
                    "telegram_name": telegram_name
                },
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
            sent = await message.answer(
                str(IncorrectPasswordException(IncorrectPasswordException(IncorrectPasswordException.__doc__))),
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
            
        await proceed_to_main_menu(user_data=user_data, message=message, state=state)
        await state.update_data(user_data=user_data, access_token=access_token)