from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from app.core.config import settings
from bot.utils.storage import CustomerText
from bot.keyboards.customer import CustomerKeyboards
from bot.keyboards.backbuttons import BackButtons

import httpx
import asyncio


router = Router()


@router.callback_query(F.data == "services")
async def get_extra_services_titles_bot_handler(callback: CallbackQuery, state: FSMContext):
    """
    По нажатию на кнопку 'Услуги' показывает все додступные услуги.

    Args:
        callback (CallbackQuery): Callback-запрос от пользователя.
        state (FSMContext): Состояние FSM и данные пользователя.
    """
    
    async with httpx.AsyncClient() as client:
        try:
            
            resp_titles = await client.get(f"{settings.BASE_FASTAPI_URL}/extra_services/")
            resp_titles.raise_for_status()
            titles = resp_titles.json()
            
            # Получение пользователя для возврата главного меню по роли
            resp_user = await client.get(f"{settings.BASE_FASTAPI_URL}/user/telegram/{callback.from_user.id}")
            resp_user.raise_for_status()
            user_data = resp_user.json()
            
        except httpx.HTTPStatusError as e:
            sent = await callback.message.answer(f"Ошибка при получении тарифов: {e}")
            await asyncio.sleep(5)
            await sent.delete()
            return
    
    sent = await callback.message.edit_text(
        CustomerText.NOTIFICATION_TEXT,
        reply_markup=await CustomerKeyboards.get_main_titles(titles=titles, callback_prefix="extra", data=user_data),
        parse_mode="HTML"
    )
    
    await state.update_data(last_bot_message=sent.message_id)
    

@router.callback_query(F.data.startswith("extra:"))
async def get_extra_services_description_bot_handler(callback: CallbackQuery, state: FSMContext):
    """
    По нажатии на какукю либо услугу, показывает её описание.

    Args:
        callback (CallbackQuery): Callback-запрос от пользователя.
        state (FSMContext): Состояние FSM и данные пользователя.
    """
    
    title = callback.data.removeprefix("extra:")
    
    async with httpx.AsyncClient() as client:
        try:
            resp_desc = await client.get(f"{settings.BASE_FASTAPI_URL}/extra_services/{title}")
            resp_desc.raise_for_status()
            description = resp_desc.json().get("description", "Описание отсутствует")
            
        except httpx.HTTPStatusError as e:
            sent = await callback.message.answer(f"Ошибка при при получении описания тарифа: {title} - {e}")
            await asyncio.sleep(5)
            await sent.delete()
            return
        
    sent = await callback.message.edit_text(
        description,
        reply_markup=await BackButtons.back_to_services(),
        parse_mode="HTML"
    )
    
    await state.update_data(last_bot_message=sent.message_id)