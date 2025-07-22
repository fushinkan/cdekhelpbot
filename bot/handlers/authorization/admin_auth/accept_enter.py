from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy import update

from app.api.handlers.get_user import UserInDB
from app.api.utils.security import verify_password
from app.db.base import async_session_factory
from app.db.models.admins import Admins
from bot.utils.bot_utils import BotUtils
from bot.utils.exceptions import AdminNotExistsException
from bot.utils.exceptions import IncorrectPasswordException
from bot.utils.state import StateUtils
from bot.keyboards.backbuttons import BackButtons
from bot.states.admin_auth import AdminAuth
from bot.handlers.authorization.main_menu import proceed_to_main_menu


router = Router()


@router.message(AdminAuth.enter_password)
async def accept_enter(message: Message, state: FSMContext):
    """
    Проверяет правильность введенного пароля и пароля сохраненного в БД.

    Args:
        message (Message): Объект входящего Telegram-сообщения от админа.
        state (FSMContext): Контейнер для хранения и управления текущим состоянием админа в рамках авторизации.

    Raises:
        AdminNotExistsException: Кастомный класс с ошибкой.
        IncorrectPasswordException: Кастомный класс с ошибкой.
    """

    data = await StateUtils.prepare_next_state(obj=message, state=state)

    try:
        data = await BotUtils.delete_error_messages(obj=message, state=state)
        
        async with async_session_factory() as session:
            admin = await UserInDB.get_admin_by_phone(phone_number=data["phone"], session=session)
            
            if not admin:
                raise AdminNotExistsException(AdminNotExistsException.__doc__)
            
            elif not verify_password(plain_password=message.text.strip(), hashed_password=admin.hashed_psw):
                raise IncorrectPasswordException(IncorrectPasswordException.__doc__)
            
            else:
                await session.execute(
                    update(Admins)
                    .where(Admins.id == data["admin_id"])
                    .values(
                        is_logged=True,
                        telegram_name=message.from_user.username,
                        telegram_id=message.from_user.id
                    )
                )
                
                await session.commit()
                
                await proceed_to_main_menu(obj=admin, message=message)
                
            await state.clear()
    
    except (AdminNotExistsException, IncorrectPasswordException) as e:
        data = await BotUtils.delete_error_messages(obj=message, state=state)
        sent = await message.answer(str(e), parse_mode="HTML", reply_markup=await BackButtons.back_to_phone())
        
        await state.update_data(error_message=sent.message_id)
        return
