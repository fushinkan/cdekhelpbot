from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.handlers.authorization.main_menu import proceed_to_main_menu
from bot.utils.state import StateUtils
from bot.states.customer import Customer
from bot.keyboards.backbuttons import BackButtons

import httpx


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
    
    if await StateUtils.edit_invoice_or_data(data=data, message=callback.message, state=state):
        return
    
    await StateUtils.push_state_to_history(state=state, new_state=Customer.contractor)
    await state.set_state(Customer.contractor)
    sent = await callback.message.answer("👤 Введите имя контрагента", reply_markup=await BackButtons.back_to_admin_panel())
    
    await state.update_data(last_bot_message=sent.message_id, role=role)
    await callback.answer()


@router.callback_query(F.data == "admin_panel")
async def admin_panel(callback: CallbackQuery, state: FSMContext):
    """
    Возвращает менеджера к админской панели

    Args:
        callback (CallbackQuery): Объект callback-запроса от пользователя.
        state (FSMContext): Текущее состояние FSM и данные пользователя.
    """
    
    data = await StateUtils.prepare_next_state(obj=callback, state=state)
    role = data.get("role", "admin")
    user_data = data
    
    await state.clear()
    
    await proceed_to_main_menu(role=role, user_data=user_data, message=callback.message)
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
