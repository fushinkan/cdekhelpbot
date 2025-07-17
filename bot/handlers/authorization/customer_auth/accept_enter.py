import asyncio
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
from bot.states.customer_auth import CustomerAuth
from bot.handlers.authorization.main_menu import proceed_to_main_menu
from bot.utils.invoice import StateUtils

router = Router()

@router.message(CustomerAuth.enter_password)
async def accept_enter(message: Message, state: FSMContext):

    data = await StateUtils.prepare_next_state(message, state)

    try:
        async with async_session_factory() as session:
            user = await UserInDB.get_client_by_phone(phone_number=data["phone"], session=session)
            
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
                        telegram_name=message.from_user.full_name,
                        telegram_id=message.from_user.id
                    )
                )
                await session.commit()
                
                await proceed_to_main_menu(user[0], message)
            await state.clear()
    
    except (UserNotExistsException, IncorrectPasswordException) as e:
        sent = await message.answer(str(e), parse_mode="HTML")
        await state.update_data(error_message=sent.message_id)
        return
    
    data = await state.get_data()
    error_message = data.get("error_message")
    
    try:
        if error_message:
            await BotUtils.delete_prev_messages(message, error_message)      
    except TelegramBadRequest:
        pass