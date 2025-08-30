from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from app.api.utils.security import Security
from app.core.config import settings
from bot.utils.state import StateUtils
from bot.keyboards.backbuttons import BackButtons
from bot.keyboards.settings import SettingsKeyboards
from bot.states.admin_auth import AdminAuth
from bot.states.customer_auth import CustomerAuth

import httpx
import asyncio


router = Router()


@router.callback_query(F.data == "settings")
async def user_settings(callback: CallbackQuery, state: FSMContext):
    """
    По нажатию на кнопку 'Настройки' переносит пользователя в настройки.
    
    Args:
        callback (CallbackQuery): Объект callback-запроса от Telegram при нажатии кнопки.
        state (FSMContext): Контейнер для хранения и управления текущим состоянием.
    """
    
    data = await StateUtils.prepare_next_state(obj=callback, state=state)
    user_data = data.get("user_data")

    sent = await callback.message.answer("⚙️ Выберите действие ниже", reply_markup=await SettingsKeyboards.main_keyboard(user_data=user_data))
    
    await state.update_data(last_bot_message=sent.message_id, user_data=user_data)
    
    
@router.callback_query(F.data == "change_password")
async def change_password(callback: CallbackQuery, state: FSMContext):
    """
    По нажатию кнопки 'Сменить пароль' запускается цепочку set_password + confirm_password

    Args:
        callback (CallbackQuery): Объект callback-запроса от Telegram при нажатии кнопки.
        state (FSMContext): Контейнер для хранения и управления текущим состоянием.
    """
    
    data = await StateUtils.prepare_next_state(obj=callback, state=state)
    user_data = data.get("user_data")
    await state.update_data(id=user_data.get("id") or user_data.get("sub"))
    
    sent = await callback.message.answer("Введите новый пароль", reply_markup=await BackButtons.back_to_settings())
    
    
    if user_data.get("role") == "admin":
        await state.set_state(AdminAuth.set_password)
    
    selected_client_id = data.get("selected_client_id") 
    if selected_client_id or user_data.get("role") == "user":
        await state.set_state(CustomerAuth.set_password)
        
    await state.update_data(last_bot_message=sent.message_id, is_change=True)