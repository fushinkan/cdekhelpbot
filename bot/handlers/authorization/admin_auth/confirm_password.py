from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlalchemy import update

from app.api.utils.security import hashed_password
from app.db.base import async_session_factory
from app.db.models.admins import Admins
from bot.states.admin_auth import AdminAuth
from bot.handlers.authorization.main_menu import proceed_to_main_menu
from bot.utils.invoice import StateUtils


router = Router()


@router.message(AdminAuth.confirm_password)
async def confirm_password(message: Message, state: FSMContext):
    """
    Подтверждает установку нового пароля для админа и записывает его в БД.

    Args:
        message (Message): Объект входящего Telegram-сообщения от админа.
        state (FSMContext): Контейнер для хранения и управления текущим состоянием админа в рамках авторизации.
    """
    
    data = await StateUtils.prepare_next_state(message, state)
    
    if message.text.strip() != data["new_password"]:
        await message.answer("Пароли не совпадают, попробуйте заново")
        await state.set_state(AdminAuth.set_password)
        return
    
    hashed_psw = hashed_password(message.text.strip())
    
    async with async_session_factory() as session:
        await session.execute(
            update(Admins)
            .where(Admins.id == int(data["admin_id"]))
            .values(
                hashed_psw=str(hashed_psw),
                telegram_name=message.from_user.full_name,
                telegram_id=message.from_user.id,
                is_logged=True
            )
        )
        
        await session.commit()
            
        admin = await session.get(Admins, data["admin_id"])
            
        await proceed_to_main_menu(admin, message)
        
        await state.clear()
