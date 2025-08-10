from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from app.core.config import settings
from bot.handlers.authorization.main_menu import proceed_to_main_menu
from bot.utils.state import StateUtils
from bot.states.customer import Customer
from bot.keyboards.backbuttons import BackButtons
from bot.utils.exceptions import CustomerAlreadyExistsException

import httpx
import asyncio


router = Router()


@router.callback_query(F.data == "add_contractor")
async def add_contractor_bot_handler(callback: CallbackQuery, state: FSMContext):
    """
    Добаление клиента в таблицу Users.

    Args:
        callback (CallbackQuery): Объект callback-запроса от пользователя.
        state (FSMContext): Текущее состояние FSM и данные пользователя.
    """
    
    data = await StateUtils.prepare_next_state(obj=callback, state=state)
    role = "admin"
    
    await StateUtils.push_state_to_history(state=state, new_state=Customer.contractor)
    await state.set_state(Customer.contractor)
    
    data = await StateUtils.prepare_next_state(obj=callback, state=state)
    
    sent = await callback.message.answer("👤 Введите имя контрагента", reply_markup=await BackButtons.back_to_admin_panel())
    
    await state.update_data(last_bot_message=sent.message_id, role=role)
    await callback.answer()


@router.callback_query(F.data.in_(["admin_panel", "cancel_customer"]))
async def admin_panel(callback: CallbackQuery, state: FSMContext):
    """
    Возвращает менеджера к админской панели

    Args:
        callback (CallbackQuery): Объект callback-запроса от пользователя.
        state (FSMContext): Текущее состояние FSM и данные пользователя.
    """
    
    data = await StateUtils.prepare_next_state(obj=callback, state=state)
    user_data = data.get("user_data")
    
    await proceed_to_main_menu(user_data=user_data, message=callback.message, state=state)
    await callback.answer()
    

@router.callback_query(F.data == "customer_summary")
async def show_customer_summary(callback: CallbackQuery, state: FSMContext):
    """
    Возвращает менеджера к сводке с новым контрагентом

    Args:
        callback (CallbackQuery): Объект callback-запроса от пользователя.
        state (FSMContext): Текущее состояние FSM и данные пользователя.
    """
    
    data = await StateUtils.prepare_next_state(obj=callback, state=state)
        
    await StateUtils.show_customer_summary(data=data, message=callback.message)

    await callback.answer()


@router.callback_query(F.data == "confirm_customer")
async def add_customer_bot_handler(callback: CallbackQuery, state: FSMContext):
    """
    По кнопке 'Подтвердить' добавляет контрагента в БД.

    Args:
        callback (CallbackQuery): Объект callback-запроса от пользователя.
        state (FSMContext): Текущее состояние FSM и данные пользователя.
    """
    
    data = await StateUtils.prepare_next_state(obj=callback, state=state)
    
    phones = [num.strip() for num in data.get("phone").split(",")]
    number_payload = [{"phone_number": phone} for phone in phones]
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{settings.BASE_FASTAPI_URL}/customers/add_customer",
                json={
                    "contractor": data.get("contractor"),
                    "contract_number": data.get("contract_number"),
                    "city": data.get("city"),
                    "number": number_payload,
                }
            )
            
            response.raise_for_status()
            
        except httpx.HTTPStatusError:
            sent = await callback.message.answer(
                str(CustomerAlreadyExistsException(CustomerAlreadyExistsException.__doc__))
            )
            
            await asyncio.sleep(3)
            await sent.delete()
            return
            
    sent = await callback.message.answer(f"Контрагент {data.get('contractor')} добавлен в базу.")
    
    await asyncio.sleep(3)
    await sent.delete()
    
    await state.clear()