import httpx
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.core.config import settings
from bot.utils.bot_utils import BotUtils
from bot.utils.state import StateUtils
from bot.states.customer_auth import CustomerAuth
from bot.states.admin_auth import AdminAuth
from bot.handlers.authorization.main_menu import proceed_to_main_menu
from bot.keyboards.backbuttons import BackButtons


router = Router()


@router.message(CustomerAuth.enter_password)
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
    user_id = data.get("user_id")
    phone = data.get("phone")
    password = message.text.strip()
    telegram_id = message.from_user.id
    telegram_name = message.from_user.username

    data = await BotUtils.delete_error_messages(obj=message, state=state)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.put(
                f"{settings.BASE_FASTAPI_URL}/auth/confirm_password",
                json={
                    "phone_number": phone,
                    "plain_password": password,
                    "telegram_id": telegram_id,
                    "telegram_name": telegram_name
                },
            )
            
            response.raise_for_status()

            response_user = await client.get(f"{settings.BASE_FASTAPI_URL}/users/{user_id}")
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
            
        except httpx.HTTPError:
            sent = await message.answer("❌ Ошибка при подтверждении пароля. Попробуйте позже.", reply_markup=await BackButtons.back_to_phone())
            await state.update_data(error_message=sent.message_id)
            return      
            
    
        data = await BotUtils.delete_error_messages(obj=message, state=state)
            
            
        await proceed_to_main_menu(role=user_data.get("role"), user_data=user_data, message=message)
        await state.clear()
        await state.set_state(CustomerAuth.main_menu)
        await state.update_data(phone=phone)