
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext


from app.db.base import async_session_factory
from app.api.handlers.get_user import UserInDB
from app.api.handlers.normalize import normalize_phone
from bot.utils.exceptions import AdminNotExistsException
from bot.keyboards.backbuttons import BackButtons

from bot.states.admin_auth import AdminAuth
from bot.utils.invoice import StateUtils

router = Router()


@router.message(AdminAuth.phone)
async def first_admin_login(message: Message, state: FSMContext):
    """
    Проверяет, нужно ли устанавливать пароль для админа.
    """
    data = await StateUtils.prepare_next_state(message, state)
    phone = data.get("phone")
    id = data.get("id")
    
    if id is None:
        await message.answer(str(AdminNotExistsException(AdminNotExistsException.__doc__)))
        return
    
    async with async_session_factory() as session:
        try:
            admin = await UserInDB.get_admin_by_id(id=id, session=session)
        except (AdminNotExistsException) as e:
            await message.answer(str(AdminNotExistsException(AdminNotExistsException.__doc__)))
            return
                
        if not admin.hashed_psw:
            sent = await message.answer("Установите пароль для безопасности",
                                    reply_markup= await BackButtons.back_to_phone())
            await state.update_data(phone=phone, admin_id=admin.id, last_bot_message=sent.message_id)
            await state.set_state(AdminAuth.set_password)
        else:
            sent = await message.answer("Введите пароль для потдверждения доступа", 
                                            reply_markup=await BackButtons.back_to_phone())
            await state.update_data(phone=phone, admin_id=admin.id, last_bot_message=sent.message_id)
            await state.set_state(AdminAuth.enter_password)

