from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext


from app.api.utils.validator import Validator
from bot.states.customer_auth import CustomerAuth
from bot.keyboards.backbuttons import BackButtons
from bot.utils.state import StateUtils
from bot.utils.bot_utils import BotUtils


router = Router()


@router.message(CustomerAuth.set_password)
async def set_client_password(message: Message, state: FSMContext):
    """
    Устанавливает пароль для пользователя, если его изначально не было.

    Args:
        message (Message): Объект входящего Telegram-сообщения от пользователя.
        state (FSMContext): Контейнер для хранения и управления текущим состоянием пользователя в рамках авторизации.
    """
    
    data = await StateUtils.prepare_next_state(obj=message, state=state)
    new_password = message.text.strip()
    
    if not Validator.validate_password(plain_password=new_password):
        data = await BotUtils.delete_error_messages(obj=message, state=state)
        sent = await message.answer("Пароль должен быть от 8 символов и более", reply_markup=await BackButtons.back_to_phone())
        
        await state.update_data(error_message=sent.message_id)
        return
    
    data = await BotUtils.delete_error_messages(obj=message, state=state)
    
    await state.update_data(new_password=new_password)
    sent = await message.answer("🔄 Введите пароль ещё раз для подтверждения",  reply_markup=await BackButtons.back_to_phone())
    await state.update_data(last_bot_message=sent.message_id)
    await state.set_state(CustomerAuth.confirm_password)