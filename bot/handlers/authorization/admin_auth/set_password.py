from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.api.utils.validator import Validator
from bot.states.admin_auth import AdminAuth
from bot.keyboards.backbuttons import BackButtons
from bot.utils.invoice import StateUtils


router = Router()


@router.message(AdminAuth.set_password)
async def set_admin_password(message: Message, state: FSMContext):
    """
    Устанавливает пароль для админа, если его изначально не было.

    Args:
        message (Message): Объект входящего Telegram-сообщения от админа.
        state (FSMContext): Контейнер для хранения и управления текущим состоянием админа в рамках авторизации.
    """
    
    data = await StateUtils.prepare_next_state(message, state)
    new_password = message.text.strip()
    
    if not Validator.validate_password(new_password):
        await message.answer("Пароль должен быть от 8 символов и более", reply_markup=await BackButtons.back_to_phone())
        return
    
    await state.update_data(new_password=new_password)
    await message.answer("🔄 Введите пароль ещё раз для подтверждения",  reply_markup=await BackButtons.back_to_phone())
    await state.set_state(AdminAuth.confirm_password)