import asyncio

from sqlalchemy import select
from aiogram.fsm.context import FSMContext
from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.db.models.admins import Admins
from app.db.models.users import Users
from app.db.base import async_session_factory
from app.api.handlers.normalize import normalize_phone
from bot.keyboards.customer import CustomerKeyboards
from bot.keyboards.backbuttons import BackButtons
from bot.keyboards.basic import BasicKeyboards
from bot.states.auth import Auth

router = Router()

    
@router.callback_query(F.data == "back_to_welcoming_screen")
async def back_to_welcoming_screen(callback: CallbackQuery, state: FSMContext):
    """
    По кнопке 'Назад' возвращает на меню приветствия.
    """
    telegram_id = callback.from_user.id
    telegram_name = callback.from_user.full_name
    
    async with async_session_factory() as session:
        
        admin = await session.execute(
            select(Admins)
            .where(Admins.telegram_id == telegram_id)
        )
        admin = admin.scalars().first()
        
        if admin:
            admin.is_logged = False
            admin.telegram_name = telegram_name

        else:
            user = await session.execute(
                select(Users)
                .where(Users.telegram_id == telegram_id)
            )   
             
            user = user.scalars().first()
            
            if user:
                user.is_logged = False
                user.telegram_name = telegram_name

        await session.commit()
    
    await asyncio.sleep(0.2)
    await state.clear()
    
    
    welcoming_text = (
        "👋 Привет!\n\n"
        "Я — электронный помощник менеджера по продажам СДЭК.\n\n"
        "Работаю по адресу:\n" 
        "Липецкая область, г. Данков,\n 1-й Спортивный переулок, 3\n\n"
        "Выбери нужный пункт меню, чтобы начать работу."
    )
    
    
    await callback.message.edit_text(welcoming_text, reply_markup=await BasicKeyboards.get_welcoming_kb())


@router.callback_query(F.data == "back_to_phone")
async def back_to_phone_screen(callback: CallbackQuery, state: FSMContext):
    """
    По кнопке 'Назад' возвращает пользователя ко вводу номера телефона.
    """
    
    await asyncio.sleep(0.2)
    await callback.answer()
    await state.clear()
    
    
    sent = await callback.message.edit_text("Отправь свой номер телефона для авторизации.", reply_markup=await BackButtons.back_to_welcoming_screen())
    
    await state.update_data(last_bot_message=sent.message_id)
    await state.set_state(Auth.waiting_for_phone)