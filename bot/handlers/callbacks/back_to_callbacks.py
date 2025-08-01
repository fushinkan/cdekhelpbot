import httpx
from aiogram.fsm.context import FSMContext
from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from app.api.utils.normalize import Normalize
from app.core.config import settings
from bot.keyboards.backbuttons import BackButtons
from bot.keyboards.basic import BasicKeyboards
from bot.keyboards.customer import CustomerKeyboards
from bot.states.invoice import InvoiceForm
from bot.states.auth import Auth
from bot.states.invoice import INVOICE_PROMPTS
from bot.states.contractor import Contractor
from bot.utils.state import StateUtils
from bot.handlers.authorization.main_menu import proceed_to_main_menu

import asyncio

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

    # Запрос в БД через эндпоинт в API
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{settings.BASE_FASTAPI_URL}/user/telegram/{telegram_id}"
            )

            response.raise_for_status()
            user_data = response.json()
            role = user_data.get("role", 'user')
            user_id = user_data.get("id")
        
            response_status = await client.put(
                f"{settings.BASE_FASTAPI_URL}/auth/{role}/{user_id}/login_status",
                json={
                    "is_logged": False,
                    "telegram_id": telegram_id,
                    "telegram_name": telegram_name
                }
            )
        
        except httpx.HTTPStatusError:
            pass
    
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
    
    data = await StateUtils.prepare_next_state(obj=callback, state=state)
    
    await asyncio.sleep(0.3)
    
    prev_state = await StateUtils.pop_state_from_history(state=state)
    
    if prev_state is None:
        phone_raw = data.get("phone")
        phone = await Normalize.normalize_phone(phone=phone_raw)
        
        await asyncio.sleep(0.2)
        await state.clear()
        await state.update_data(phone=phone)
    
        main_menu = (
            "👋 Приветствую!\n\n"
            "Здесь ты можешь быстро оформить накладную, подобрать тарифы и подключить дополнительные услуги. 🚀\n"
            "Не нужно ломать голову — просто выбери, что нужно, и я всё сделаю быстро и без лишних хлопот! 💼✨\n"
            "Если возникнут вопросы — пиши, всегда рад помочь! 😊👍"
        )

        await callback.message.answer(main_menu, reply_markup=await CustomerKeyboards.customer_kb())
        return 
    
    await state.set_state(prev_state)
    
    prompt = INVOICE_PROMPTS.get(prev_state.state)
    if prompt is None:
        await callback.answer("⚠️ Попробуйте заново ввести данные.")
        return
    
    text, keyboard_coroutine = prompt
    keyboard = await keyboard_coroutine()

    sent = await callback.message.answer(text, reply_markup=keyboard)

    await state.update_data(last_bot_message=sent.message_id)
    

@router.callback_query(F.data == "back_to_summary")
async def back_to_summary(callback: CallbackQuery, state: FSMContext):
    """
    Возвращает пользователя к полной сводке при нажатии кнопки 'Назад' и сбрасывает режим редактирования.

    Args:
        callback (CallbackQuery): Объект callback-запроса от пользователя.
        state (FSMContext): Текущее состояние FSM и данные пользователя.
    """
    
    data = await StateUtils.prepare_next_state(obj=callback, state=state)
        
    await state.set_state(InvoiceForm.confirmation)
    await state.update_data(editing_field=None)

    await StateUtils.get_summary(message=callback.message, data=data)


@router.callback_query(F.data == "back_to_contractor_phone")
async def back_to_contractor_phone_form(callback: CallbackQuery, state: FSMContext):
    """
    По кнопке 'Назад' возвращает пользователя к этапу ввода номера телефона для заключения договора.

    Args:
        callback (CallbackQuery): Объект callback-запроса от пользователя.
        state (FSMContext): Текущее состояние FSM и данные пользователя.
    """
    
    sent = await callback.message.edit_text("Введите Ваш номер телефона", reply_markup=await BackButtons.back_to_welcoming_screen())
    await state.set_state(Contractor.phone)
    
    
@router.callback_query(F.data == "back_to_contractor_summary")
async def back_to_summary(callback: CallbackQuery, state: FSMContext):
    """
    Возвращает пользователя к полной сводке при нажатии кнопки 'Назад' и сбрасывает режим редактирования.

    Args:
        callback (CallbackQuery): Объект callback-запроса от пользователя.
        state (FSMContext): Текущее состояние FSM и данные пользователя.
    """
    
    data = await StateUtils.prepare_next_state(obj=callback, state=state)
        
    await state.set_state(Contractor.tin_and_confirmation)
    await state.update_data(editing_field=None)

    await StateUtils.get_contractor_summary(message=callback.message, data=data)
    
    
@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    
    data = await StateUtils.prepare_next_state(obj=callback, state=state)
    phone_number = data.get("phone")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{settings.BASE_FASTAPI_URL}/user/phone/{phone_number}")
            
            response.raise_for_status()
            
            user_data = response.json()
            role = user_data.get("role", None)
        
        except httpx.HTTPError:
            await callback.message.answer("❌ Не удалось получить информацию о пользователе. Попробуйте позже.")
            return
        
        await state.clear()
        await state.update_data(phone=phone_number)
        await proceed_to_main_menu(role=role, user_data=user_data, message=callback.message)