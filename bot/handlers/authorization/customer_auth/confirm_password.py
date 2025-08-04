from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.core.config import settings
from bot.keyboards.backbuttons import BackButtons
from bot.states.customer_auth import CustomerAuth
from bot.handlers.authorization.main_menu import proceed_to_main_menu
from bot.utils.state import StateUtils
from bot.utils.exceptions import RequestErrorException

import httpx


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
    phone = data.get("phone")
    telegram_id = message.from_user.id
    user_id = data.get("id")
    first_password = data.get('new_password')
    second_psw = message.text.strip()
    
    if first_password != second_psw:
        data = await StateUtils.prepare_next_state(obj=message, state=state)
        sent = await message.answer("Пароли не совпадают, попробуйте заново", reply_markup=await BackButtons.back_to_phone())
        
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
                    "confirm_password": second_psw
                }
            )
            
            response.raise_for_status()

            response_user = await client.get(f"{settings.BASE_FASTAPI_URL}/user/{user_id}")
            response_user.raise_for_status()
            user_data = response_user.json()
            
            role = user_data.get("role")
            telegram_id = telegram_id
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
            
            
        await proceed_to_main_menu(role=user_data.get("role"), user_data=user_data, message=message)
        await state.clear()
        await state.set_state(CustomerAuth.main_menu)
        await state.update_data(phone=phone) 