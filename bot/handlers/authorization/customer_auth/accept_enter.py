from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy import update

from app.api.handlers.get_user import UserInDB
from app.api.utils.security import verify_password
from app.db.base import async_session_factory
from app.db.models.users import Users
from bot.utils.bot_utils import BotUtils
from bot.utils.exceptions import UserNotExistsException
from bot.utils.exceptions import IncorrectPasswordException
from bot.utils.state import StateUtils
from bot.states.customer_auth import CustomerAuth
from bot.handlers.authorization.main_menu import proceed_to_main_menu


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
    phone = data.get("phone")

    try:
        data = await BotUtils.delete_error_messages(obj=message, state=state)
        
        async with async_session_factory() as session:
            user = await UserInDB.get_client_by_phone(phone_number=phone, session=session)
            
            if not user:
                raise UserNotExistsException(UserNotExistsException.__doc__)
            
            elif not verify_password(plain_password=message.text.strip(), hashed_password=user[0].hashed_psw):
                raise IncorrectPasswordException(IncorrectPasswordException.__doc__)
            
            else:
                await session.execute(
                    update(Users)
                    .where(Users.id == data["user_id"])
                    .values(
                        is_logged=True,
                        telegram_name=message.from_user.username,
                        telegram_id=message.from_user.id
                    )
                )
                
                await session.commit()
                
                await proceed_to_main_menu(obj=user[0], message=message)
                
            await state.clear()
            await state.set_state(CustomerAuth.main_menu)
            await state.update_data(phone=phone)
    
    except (UserNotExistsException, IncorrectPasswordException) as e:
        data = await BotUtils.delete_error_messages(obj=message, state=state)
        sent = await message.answer(str(e), parse_mode="HTML")
        await state.update_data(error_message=sent.message_id)
        return