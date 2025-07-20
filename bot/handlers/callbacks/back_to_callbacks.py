import asyncio

from sqlalchemy import select
from aiogram.fsm.context import FSMContext
from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.api.handlers.normalize import normalize_phone
from app.db.models.admins import Admins
from app.db.models.users import Users
from app.db.base import async_session_factory
from bot.keyboards.backbuttons import BackButtons
from bot.keyboards.basic import BasicKeyboards
from bot.keyboards.customer import CustomerKeyboards
from bot.states.auth import Auth
from bot.states.invoice import INVOICE_PROMPTS
from bot.utils.invoice import StateUtils


router = Router()

    
@router.callback_query(F.data == "back_to_welcoming_screen")
async def back_to_welcoming_screen(callback: CallbackQuery, state: FSMContext):
    """
    По кнопке 'Назад' возвращает пользователя в меню приветствия и сбрасывает статус авторизации в БД.

    Args:
        callback (CallbackQuery): Объект callback-запроса от пользователя.
        state (FSMContext): Текущее состояние FSM и данные пользователя.
    """
    
    telegram_id = callback.from_user.id
    telegram_name = callback.from_user.username
    
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
    По кнопке 'Назад' переводит пользователя к вводу номера телефона для повторной авторизации.

    Args:
        callback (CallbackQuery): Объект callback-запроса от пользователя.
        state (FSMContext): Текущее состояние FSM и данные пользователя.
    """
    
    await asyncio.sleep(0.2)
    await callback.answer()
    await state.clear()
    
    sent = await callback.message.edit_text("Отправь свой номер телефона для авторизации.", reply_markup=await BackButtons.back_to_welcoming_screen())
    
    await state.update_data(last_bot_message=sent.message_id)
    await state.set_state(Auth.waiting_for_phone)
    
    
@router.callback_query(F.data.startswith("go_back_to_"))
async def go_back(callback: CallbackQuery, state: FSMContext):
    """
    Откатывает пользователя к предыдущему состоянию в истории или к главному меню, если истории нет.

    Args:
        callback (CallbackQuery): Объект callback-запроса от пользователя.
        state (FSMContext): Текущее состояние FSM и данные пользователя.
    """
    
    data = await state.get_data()
    
    await asyncio.sleep(0.3)
    
    prev_state = await StateUtils.pop_state_from_history(state=state)
    
    if prev_state is None:
        phone_raw = data.get("phone")
        phone = await normalize_phone(phone=phone_raw)
        
        await asyncio.sleep(0.2)
        await state.clear()
        await state.update_data(phone=phone)
    
        main_menu = (
            "👋 Приветствую!\n\n"
            "Здесь ты можешь быстро оформить накладную, подобрать тарифы и подключить дополнительные услуги. 🚀\n"
            "Не нужно ломать голову — просто выбери, что нужно, и я всё сделаю быстро и без лишних хлопот! 💼✨\n"
            "Если возникнут вопросы — пиши, всегда рад помочь! 😊👍"
        )
    
        await callback.message.edit_text(main_menu, reply_markup=await CustomerKeyboards.customer_kb())
        return 
    
    await state.set_state(prev_state)
    
    prompt = INVOICE_PROMPTS.get(prev_state.state)
    if prompt is None:
        await callback.answer("⚠️ Попробуйте заново ввести данные.")
        return
    
    text, keyboard_coroutine = prompt
    keyboard = await keyboard_coroutine()
    sent = await callback.message.edit_text(text, reply_markup=keyboard)
    
    await state.update_data(last_bot_message=sent.message_id)