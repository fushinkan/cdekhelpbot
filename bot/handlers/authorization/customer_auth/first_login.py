
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext


from app.db.base import async_session_factory
from app.api.handlers.get_user import UserInDB
from bot.utils.exceptions import UserNotExistsException
from bot.keyboards.backbuttons import BackButtons

from bot.states.customer_auth import CustomerAuth
from bot.utils.invoice import StateUtils


router = Router()


@router.message(CustomerAuth.phone)
async def first_client_login(message: Message, state: FSMContext):
    """
    Обрабатывает ввод номера телефона при первичной авторизации пользователя.
    
    Args:
        message (Message): Объект входящего Telegram-сообщения от пользователя.
        state (FSMContext): Контейнер для хранения и управления текущим состоянием пользователя в рамках авторизации.
    """
    
    data = await StateUtils.prepare_next_state(obj=message, state=state)
    phone = data.get("phone")
    id = data.get("id")
    
    if id is None:
        await message.answer(str(UserNotExistsException(UserNotExistsException.__doc__)))
        return
    
    async with async_session_factory() as session:

        try:
            user = await UserInDB.get_client_by_id(id=id, session=session)
        except UserNotExistsException:
            await message.answer(str(UserNotExistsException(UserNotExistsException.__doc__)))

        if not user[0].hashed_psw:
            sent = await message.answer("Установите пароль для безопасности",
                                    reply_markup= await BackButtons.back_to_phone())
            
            await state.update_data(phone=phone, user_id=user[0].id, last_bot_message=sent.message_id)
            await state.set_state(CustomerAuth.set_password)
            
        else:
            sent = await message.answer("Введите пароль для потдверждения доступа", 
                                            reply_markup=await BackButtons.back_to_phone())
            
            await state.update_data(phone=phone, user_id=user[0].id, last_bot_message=sent.message_id)
            await state.set_state(CustomerAuth.enter_password)

