from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from app.core.config import settings
from bot.keyboards.customer import CustomerKeyboards
from bot.utils.exceptions import EmptyHistoryException
from bot.utils.state import StateUtils
from bot.handlers.authorization.main_menu import proceed_to_main_menu

import httpx
import asyncio


router = Router()


@router.callback_query(F.data == "history")
async def show_user_orders_all_years_bot_handler(callback: CallbackQuery, state: FSMContext):
    """
    По кнопке 'История' показывает пользователю года заказов.

    Args:
        callback (CallbackQuery): Callback-запрос от пользователя.
        state (FSMContext): Состояние FSM и данные пользователя.
    """
    
    data = await StateUtils.prepare_next_state(obj=callback, state=state)

    user_data = data.get("user_data")
    telegram_id = user_data["telegram_id"] or callback.from_user.id
    user_id = user_data.get("id") 
    
    selected_client_id = data.get("selected_client_id")

    if selected_client_id:
        user_id = selected_client_id
    
    async with httpx.AsyncClient() as client:
        try:
            # Получение user_id по Telegram ID
            resp_user = await client.get(f"{settings.BASE_FASTAPI_URL}/user/telegram/{telegram_id}")
            resp_user.raise_for_status()
            user_data = resp_user.json()
            user_id = user_data.get("id", None)
            user_data["selected_client_id"] = user_id
            # Получение заказов по годам
            resp_years = await client.get(f"{settings.BASE_FASTAPI_URL}/history/{user_id}")
            resp_years.raise_for_status()
            years = resp_years.json().get("order_years", None)
            
        except httpx.HTTPStatusError as e:
            # Если история пуста (404)
            if e.response.status_code == 404:
                sent = await callback.message.answer(
                    str(EmptyHistoryException(EmptyHistoryException.__doc__))
                )
             
            else:
                sent = await callback.message.answer(f"Непредвиденная ошибка: {e}")
                
            await asyncio.sleep(5)
            await sent.delete()
            
            menu = await proceed_to_main_menu(message=callback.message, user_data=user_data, state=state)

            await state.update_data(last_bot_message=menu.message_id)
            return
        

    sent = await callback.message.answer(
        "🗓️ Выберите год, чтобы посмотреть историю заказов.",
        reply_markup=await CustomerKeyboards.get_years_keyboard(years=years, data=user_data)
    )
    
    await callback.answer()
    await state.update_data(last_bot_message=sent.message_id, user_data=user_data)
    

@router.callback_query(F.data.startswith("year:"))
async def show_months_by_year(callback: CallbackQuery, state: FSMContext):
    """
    По нажатию на какой либо год, показывает месяцы, в которые были сделаны заказы.

    Args:
        callback (CallbackQuery): Callback-запрос от пользователя.
        state (FSMContext): Состояние FSM и данные пользователя.
    """
    
    data = await StateUtils.prepare_next_state(obj=callback, state=state)

    year = int(callback.data.split(":")[1])
    user_data = data.get("user_data")
    user_id = data.get("selected_client_id") or user_data["id"]
    
    
    async with httpx.AsyncClient() as client:
        try:
            resp_months = await client.get(f"{settings.BASE_FASTAPI_URL}/history/{user_id}/{year}")
            resp_months.raise_for_status()
            months = resp_months.json().get("order_months")
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                sent = await callback.message.answer("Нет заказов за выбранный год.")
            else:
                sent = await callback.message.answer(f"Ошибка: {e}")
            await asyncio.sleep(5)
            await sent.delete()
            return
    
    sent = await callback.message.answer(
        f"🗓️ Выберите месяц {year} года, чтобы посмотреть историю заказов.",
        reply_markup=await CustomerKeyboards.get_months_by_year_keyboard(months=months, year=year, data=user_data)
    )
    
    await callback.answer()
    await state.update_data(last_bot_message=sent.message_id, user_data=user_data)
    

@router.callback_query(F.data.startswith("month:"))
async def get_user_invoices_by_month_year(callback: CallbackQuery, state: FSMContext):
    """
    По нажатию на какой либо месяц, показывает накладные за этот период.

    Args:
        callback (CallbackQuery): Callback-запрос от пользователя.
        state (FSMContext): Состояние FSM и данные пользователя.
    """
    
    data = await StateUtils.prepare_next_state(obj=callback, state=state)

    user_data = data.get("user_data")
    user_id = data.get("selected_client_id") or user_data["id"]
    _, year_raw, month_raw = callback.data.split(":") 
    year, month = int(year_raw), int(month_raw)
    
    async with httpx.AsyncClient() as client:
        try:
            resp_inv = await client.get(f"{settings.BASE_FASTAPI_URL}/history/{user_id}/{year}/{month}")
            resp_inv.raise_for_status()
            invoices = resp_inv.json().get("invoices")
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                sent = await callback.message.answer("❌ Накладных за этот месяц не найдено.")
            else:
                sent = await callback.message.answer(f"Ошибка при получении данных: {e}")
            await asyncio.sleep(5)
            await sent.delete()
            return
        
    sent = await callback.message.answer(
        f"📦 Вот накладные за {month:02}.{year}",
        reply_markup=await CustomerKeyboards.get_invoices_by_month_year_keyboard(
            invoices=invoices,  
            year=year
        )
    )

    await state.update_data(last_bot_message=sent.message_id)
    

@router.callback_query(F.data.startswith("invoice:"))
async def download_invoice_bot_handler(callback: CallbackQuery, state: FSMContext):
    """
    По нажатию на накладную скачивает ее.

    Args:
        callback (CallbackQuery): Callback-запрос от пользователя.
        state (FSMContext): Состояние FSM и данные пользователя.
    """
    
    invoice_id = int(callback.data.split(":")[1])    
    
    async with httpx.AsyncClient() as client:
        try:
            resp_inv = await client.get(f"{settings.BASE_FASTAPI_URL}/history/download/{invoice_id}")
            resp_inv.raise_for_status()
            telegram_file_id = resp_inv.json().get("telegram_file_id")
            
            sent = await callback.message.answer_document(
                document=telegram_file_id,
                caption="📦 Ваша накладная"
            )
            
            await callback.answer()
            await state.update_data(last_bot_message=sent.message_id)
        
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                sent = await callback.message.answer(f"Ошибка скачивания файла: {e}")
                await asyncio.sleep(5)
                await sent.delete()
                return
            
        except Exception as e:
            sent = await callback.message.answer(f"⚠️ Ошибка: {e}")
            await asyncio.sleep(5)
            await sent.delete()
            return