import httpx
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.core.config import settings
from app.api.utils.validator import Validator
from bot.states.customer_auth import CustomerAuth
from bot.keyboards.backbuttons import BackButtons
from bot.utils.state import StateUtils
from bot.utils.bot_utils import BotUtils
from bot.utils.exceptions import RequestErrorException, InvalidPasswordException


router = Router()


@router.message(CustomerAuth.set_password)
async def set_client_password(message: Message, state: FSMContext):
    """
    Устанавливает пароль для пользователя через FastAPI, если его изначально не было.
    """
    
    data = await StateUtils.prepare_next_state(obj=message, state=state)
    phone = data.get("phone")
    user_id = data.get("id")
    telegram_id = message.from_user.id
    new_password = message.text.strip()

    if not Validator.validate_password(plain_password=new_password):
        data = await StateUtils.prepare_next_state(obj=message, state=state)
        sent = await message.answer(
            str(InvalidPasswordException(InvalidPasswordException.__doc__)), 
            reply_markup=await BackButtons.back_to_phone()
        )
        await state.update_data(error_message=sent.message_id)
        return

    await StateUtils.prepare_next_state(obj=message, state=state)

    # Запрос в БД через эндпоинт в API
    async with httpx.AsyncClient() as client:
        try:
            response = await client.put(
                f"{settings.BASE_FASTAPI_URL}/auth/set_password",
                json={"user_id": user_id, "plain_password": new_password}
            )
            response.raise_for_status()
            
        except httpx.HTTPStatusError:
            data = await StateUtils.prepare_next_state(obj=message, state=state)
            sent = await message.answer(
                "❌ Ошибка при установке пароля. Попробуйте заново",
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

    sent = await message.answer("✅ Пароль установлен. Введите его ещё раз для входа.",
                                reply_markup=await BackButtons.back_to_phone())
    
    await state.update_data(last_bot_message=sent.message_id, phone=phone, new_password=new_password)
    await state.set_state(CustomerAuth.confirm_password)
