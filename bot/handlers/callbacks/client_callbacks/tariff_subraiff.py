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


@router.callback_query(F.data == "tariffs")
async def show_main_tariffs_bot_handler(callback: CallbackQuery, state: FSMContext):
    """
    По кнопке 'Тарифы' показывает клиенту доступные тарифы.
    
    Args:
        callback (CallbackQuery): Callback-запрос от пользователя.
        state (FSMContext): Состояние FSM и данные пользователя.
    """
    
    async with httpx.AsyncClient() as client:
        try:
            # Получение информации о тарифах
            response = await client.get(f"{settings.BASE_FASTAPI_URL}/tariffs/main")
            response.raise_for_status()
            main_titles = response.json()
            
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
        reply_markup=await CustomerKeyboards.get_main_titles(titles=main_titles, data=user_data, callback_prefix="tariff"),
        parse_mode="HTML"
    )
    
    await state.update_data(last_bot_message=sent.message_id, user_data=user_data)


@router.callback_query(F.data.startswith("tariff:"))
async def get_tariff_description_bot_handler(callback: CallbackQuery, state: FSMContext):
    """
    По нажатию на тариф показывает описание тарифа.
    
    Args:
        callback (CallbackQuery): Callback-запрос от пользователя.
        state (FSMContext): Состояние FSM и данные пользователя.
    """
    
    title = callback.data.removeprefix("tariff:")  

    async with httpx.AsyncClient() as client:
        if title.lower() == "«доставка до маркетплейсов»":

            try:
                # Получение списка подвариантов
                resp_sub = await client.get(f"{settings.BASE_FASTAPI_URL}/tariffs/sub")
                resp_sub.raise_for_status()
                sub_titles = resp_sub.json()  # Ожидается список подвариантов
                
                # Получение инфмарации о тарифе "Доставка до маркетплейсов"
                resp_main = await client.get(rf"{settings.BASE_FASTAPI_URL}/tariffs/{title}")
                resp_main.raise_for_status()
                main_desc = resp_main.json().get("description", "Описание отсутствует.")

            except httpx.HTTPStatusError as e:
                sent = await callback.message.answer(f"Ошибка при получении данных: {e}")
                await asyncio.sleep(5)
                await sent.delete()
                return 

            sent = await callback.message.edit_text(
                text=main_desc,
                reply_markup=await CustomerKeyboards.get_sub_titles(subtitles=sub_titles, callback_prefix="subtariff"),
                parse_mode="HTML"
            )
            
            await state.update_data(last_bot_message=sent.message_id)
            
        else:
            
            try:
                response = await client.get(f"{settings.BASE_FASTAPI_URL}/tariffs/{title}")
                response.raise_for_status()
                main_data = response.json()
                description = main_data.get("description", "Описание отсутствует.")
            except httpx.HTTPStatusError as e:
                sent = await callback.message.answer(f"Ошибка при получении описания тарифа: {title} - {e}")
                await asyncio.sleep(5)
                await sent.delete()
                return

            sent = await callback.message.edit_text(
                text=description,
                reply_markup=await BackButtons.back_to_tariffs(),
                parse_mode="HTML",
            )
            
            await state.update_data(last_bot_message=sent.message_id)
            
            
@router.callback_query(F.data.startswith("subtariff:"))
async def get_sub_tariff_title_bot_handler(callback: CallbackQuery, state: FSMContext):
    """
    Обрабатывает кнопки внутри тарифа 'Доставка до маркетплесов'.

    Args:
        callback (CallbackQuery): Callback-запрос от пользователя.
        state (FSMContext): Состояние FSM и данные пользователя.
    """
    
    sub_title = callback.data.removeprefix("subtariff:")
    
    async with httpx.AsyncClient() as client:
        try:
            resp_sub_title = await client.get(f"{settings.BASE_FASTAPI_URL}/tariffs/{sub_title}")
            resp_sub_title.raise_for_status()
            description = resp_sub_title.json().get("description", "Описание отсутствует")
            
        except httpx.HTTPStatusError as e:
            sent = await callback.message.answer(f"Ошибка при при получении описания тарифа: {sub_title} - {e}")
            await asyncio.sleep(5)
            await sent.delete()
            return

    sent = await callback.message.edit_text(
        description,
        reply_markup=await CustomerKeyboards.get_back_to_parent_tariff(parent_tariff="«Доставка до маркетплейсов»"),
        parse_mode='HTML'
    )
    
    await state.update_data(last_bot_message=sent.message_id)