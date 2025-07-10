import asyncio
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram import Router
from aiogram.types import Message
from sqlalchemy import update

from app.api.utils.security import verify_password
from app.db.base import async_session_factory
from app.api.handlers.get_user import UserInDB
from app.db.models.admins import Admins
from app.db.models.users import Users
from bot.utils.exceptions import IncorrectPasswordException
from bot.keyboards.admin import AdminKeyboards
from bot.keyboards.customer import CustomerKeyboards
from bot.utils.bot_utils import BotUtils
from bot.states.admin_auth import AdminAuth
from bot.utils.exceptions import UserNotExistsException
from bot.keyboards.backbuttons import BackButtons

router = Router()


@router.message(AdminAuth.password)
async def process_password(message: Message, state: FSMContext):
    """
    Проверяет корректность введенного пароля.
    """
    
    await asyncio.sleep(0.2)
    
    
    data = await state.get_data()
    last_bot_message_id = data.get("last_bot_message")
    role = data.get("role")
    phone = data.get("phone")
    
    async with async_session_factory() as session:
        if role == "admin":
            user = await UserInDB.get_admin_by_phone(phone_number=phone, session=session)
        elif role == "user":
            user = await UserInDB.get_client_by_phone(phone_number=phone, session=session)
        else:
            user = None
    
        
        if role is None and phone is None and user is None:
            sent = await message.answer(UserNotExistsException(UserNotExistsException.__doc__))
            await asyncio.sleep(3)
            await message.delete()
            await sent.delete()
            await state.clear()
            return
        
        
        entered_password = message.text.strip()
        
        
        try:
            if last_bot_message_id:
                await BotUtils.delete_prev_messages(obj=message, message_id=last_bot_message_id)
        except TelegramBadRequest:
            pass
        
        
        if verify_password(entered_password, user.hashed_psw):
            if role == "admin":
                await session.execute(
                    update(Admins)
                    .where(Admins.id == user.id)
                    .values(
                        telegram_id=message.from_user.id,
                        telegram_name=message.from_user.full_name,
                        is_logged=True
                    )
                )
                
                sent = await message.answer((
                    f"👋 Здравствуйте, {user.contractor}\n\n"
                    "Добро пожаловать в панель управления.\n"
                    "Здесь вы можете управлять пользователями и контролировать систему.\n"
                    "Выберите нужный пункт меню, чтобы начать работу."
                ), reply_markup=await AdminKeyboards.get_admin_kb())
                await message.delete()
                await state.clear()
                    
            elif role == "user":
                await session.execute(
                    update(Users)
                    .where(Users.id == user.id)
                    .values(
                        telegram_id=message.from_user.id,
                        telegram_name=message.from_user.full_name,
                        is_logged=True  
                    )
                )
                
                sent = await message.answer((
                "👋 Приветствую!\n\n"
                "Здесь ты можешь быстро оформить накладную, подобрать тарифы и подключить дополнительные услуги. 🚀\n"
                "Не нужно ломать голову — просто выбери, что нужно, и я всё сделаю быстро и без лишних хлопот! 💼✨\n"
                "Если возникнут вопросы — пиши, всегда рад помочь! 😊👍"
            ), reply_markup=await CustomerKeyboards.customer_kb())
                
                await asyncio.sleep(1)

                await state.clear()
                await state.update_data(phone=phone)
                
            await session.commit()
            
            
        else:
            sent = await message.answer(str(IncorrectPasswordException(IncorrectPasswordException.__doc__)), parse_mode="HTML", reply_markup=await BackButtons.back_to_phone())
            await state.update_data(last_bot_message=sent.message_id)

    
        
    

    
    

    
 