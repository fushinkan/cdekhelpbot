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
        await BotUtils.delete_error_messages(obj=message, state=state)
        sent = await message.answer("Пароль должен быть от 8 символов и более", reply_markup=await BackButtons.back_to_phone())
        await state.update_data(error_message=sent.message_id)
        return

    await BotUtils.delete_error_messages(obj=message, state=state)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.put(
                f"{settings.BASE_FASTAPI_URL}/auth/set_password",
                json={"telegram_id": telegram_id, "plain_password": new_password}
            )
            response.raise_for_status()
            
        except httpx.HTTPError as e:
            sent = await message.answer("❌ Ошибка при установке пароля. Попробуйте позже.",
                                        reply_markup=await BackButtons.back_to_phone())
            await state.update_data(error_message=sent.message_id)
            return

    sent = await message.answer("✅ Пароль установлен. Введите его ещё раз для входа.",
                                reply_markup=await BackButtons.back_to_phone())
    
    await state.update_data(last_bot_message=sent.message_id, phone=phone)
    await state.set_state(CustomerAuth.confirm_password)
