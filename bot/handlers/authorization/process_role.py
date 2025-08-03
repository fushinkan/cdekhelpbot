import httpx
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.core.config import settings
from app.api.utils.normalize import Normalize
from bot.utils.exceptions import IncorrectPhoneException
from bot.utils.state import StateUtils
from bot.utils.bot_utils import BotUtils
from bot.states.auth import Auth
from bot.states.admin_auth import AdminAuth
from bot.states.customer_auth import CustomerAuth
from bot.handlers.authorization.first_login import first_client_login
from bot.keyboards.backbuttons import BackButtons
from bot.utils.exceptions import UserNotExistsException, RequestErrorException


router = Router()


@router.message(Auth.waiting_for_phone)
async def process_role(message: Message, state: FSMContext):
    """
    Определяет роль пользователя (admin/user).

    Args:
        message (Message): Объект входящего Telegram-сообщения от пользователя/админа.
        state (FSMContext): Контейнер для хранения и управления текущим состоянием пользователя/админа в рамках авторизации.
    """
    
    data = await StateUtils.prepare_next_state(obj=message, state=state)
    phone_number = message.text.strip()
    
    try:
        phone = await Normalize.normalize_phone(phone=phone_number)

    except IncorrectPhoneException as e:
        data = await StateUtils.prepare_next_state(obj=message, state=state)
        sent = await message.answer(str(e), parse_mode="HTML")
        
        await state.update_data(error_message=sent.message_id)
        
        return
    
    data = await StateUtils.prepare_next_state(obj=message, state=state)
    
    # Запрос в БД через эндпоинт в API
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{settings.BASE_FASTAPI_URL}/user/phone/{phone_number}")
            response.raise_for_status()
            data = response.json()
            role = data["role"]
            user_id = data["id"]
            
        except httpx.HTTPStatusError:
            data = await StateUtils.prepare_next_state(obj=message, state=state)
            sent = await message.answer(
                str(UserNotExistsException(UserNotExistsException.__doc__)),
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
        
    if role == "admin":
            await state.set_state(AdminAuth.phone)
            await state.update_data(phone=phone, id=user_id)
            await first_client_login(message=message, state=state)
    elif role == "user":
            await state.set_state(CustomerAuth.phone)
            await state.update_data(phone=phone, id=user_id)
            await first_client_login(message=message, state=state)