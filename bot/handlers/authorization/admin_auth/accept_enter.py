from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.core.config import settings
from bot.utils.state import StateUtils
from bot.states.admin_auth import AdminAuth
from bot.handlers.authorization.main_menu import proceed_to_main_menu
from bot.keyboards.backbuttons import BackButtons
from bot.utils.exceptions import RequestErrorException, IncorrectPasswordException

import httpx


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

            response_user = await client.get(f"{settings.BASE_FASTAPI_URL}/user/{user_id}")
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
            data = await StateUtils.prepare_next_state(obj=message, state=state)
            sent = await message.answer(
                str(IncorrectPasswordException(IncorrectPasswordException(IncorrectPasswordException.__doc__))),
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
            
            
        await proceed_to_main_menu(role=user_data.get("role"), user_data=user_data, message=message)
        await state.clear()