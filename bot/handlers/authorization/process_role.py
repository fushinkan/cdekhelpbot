from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.api.handlers.normalize import normalize_phone
from app.db.base import async_session_factory
from app.api.handlers.get_user import UserInDB
from bot.utils.exceptions import UserNotExistsException, AdminNotExistsException
from bot.utils.invoice import StateUtils
from bot.states.auth import Auth
from bot.states.admin_auth import AdminAuth
from bot.states.customer_auth import CustomerAuth
from bot.handlers.authorization.admin_auth.first_login import first_admin_login
from bot.handlers.authorization.customer_auth.first_login import first_client_login
from bot.keyboards.backbuttons import BackButtons


router = Router()


@router.message(Auth.waiting_for_phone)
async def process_role(message: Message, state: FSMContext):
    """
    Определяет роль пользователя (admin/user).

    Args:
        message (Message): Объект входящего Telegram-сообщения от пользователя/админа.
        state (FSMContext): Контейнер для хранения и управления текущим состоянием пользователя/админа в рамках авторизации.
    """
    
    phone = await normalize_phone(phone=message.text.strip())
    await StateUtils.prepare_next_state(obj=message, state=state)

    async with async_session_factory() as session:
        admin = None
        user = None
        
        admin_flag = False
        user_flag = False
        
        try:
            admin = await UserInDB.get_admin_by_phone(phone_number=phone, session=session)
            
            if admin.role == "admin":
                await state.set_state(AdminAuth.phone)
                await state.update_data(phone=phone, id=admin.id)
                await first_admin_login(message=message, state=state)
                return
            
        except AdminNotExistsException as e:
                admin_flag = True
        
        try:
            user = await UserInDB.get_client_by_phone(phone_number=phone, session=session)
            
            if user and user[0].role == "user":
                await state.set_state(CustomerAuth.phone)
                await state.update_data(phone=phone, id=user[0].id)
                await first_client_login(message=message, state=state)
                return
            
        except UserNotExistsException as e:
                user_flag = True
                     
        if admin_flag and user_flag:
            sent = await message.answer("Пользователь не найден. Попробуйте заново.", reply_markup=await BackButtons.back_to_welcoming_screen())
            await state.update_data(last_bot_message=sent.message_id)
            return
