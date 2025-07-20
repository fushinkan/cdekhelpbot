from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlalchemy import update

from app.api.utils.security import hashed_password
from app.db.base import async_session_factory
from app.db.models.users import Users
from bot.states.customer_auth import CustomerAuth
from bot.handlers.authorization.main_menu import proceed_to_main_menu
from bot.utils.invoice import StateUtils


router = Router()


@router.message(CustomerAuth.confirm_password)
async def confirm_password(message: Message, state: FSMContext):
    """
    Подтверждает установку нового пароля для пользователя и записывает его в БД.

    Args:
        message (Message): Объект входящего Telegram-сообщения от пользователя.
        state (FSMContext): Контейнер для хранения и управления текущим состоянием пользователя в рамках авторизации.
    """
    
    data = await StateUtils.prepare_next_state(obj=message, state=state)
    phone = data.get("phone")
    
    if message.text.strip() != data["new_password"]:
        await message.answer("Пароли не совпадают, попробуйте заново")
        await state.set_state(CustomerAuth.set_password)
        return
    
    hashed_psw = hashed_password(password=message.text.strip())
    
    async with async_session_factory() as session:
        await session.execute(
            update(Users)
            .where(Users.id == int(data["user_id"]))
            .values(
                hashed_psw=str(hashed_psw),
                telegram_name=message.from_user.username,
                telegram_id=message.from_user.id,
                is_logged=True
        )
            )
        
        await session.commit()
            
        user = await session.get(Users, data["user_id"])
            
        await proceed_to_main_menu(obj=user, message=message)
        await state.clear()
        await state.set_state(CustomerAuth.main_menu)
        await state.update_data(phone=phone)
