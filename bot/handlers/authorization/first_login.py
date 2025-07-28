import httpx
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.core.config import settings
from bot.utils.exceptions import UserNotExistsException
from bot.keyboards.backbuttons import BackButtons
from bot.states.admin_auth import AdminAuth
from bot.states.customer_auth import CustomerAuth
from bot.utils.state import StateUtils


router = Router()


@router.message(CustomerAuth.phone)
async def first_client_login(message: Message, state: FSMContext):
    """
    Обрабатывает ввод номера телефона при первичной авторизации пользователя.
    
    Args:
        message (Message): Объект входящего Telegram-сообщения от пользователя.
        state (FSMContext): Контейнер для хранения и управления текущим состоянием пользователя в рамках авторизации.
    """
    

    data = await StateUtils.prepare_next_state(obj=message, state=state)
    phone_number = data.get("phone")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{settings.BASE_FASTAPI_URL}/auth/phone/{phone_number}")
            response.raise_for_status()
            user = response.json()
        except httpx.HTTPStatusError as e:
            await message.answer(f"Пользователь с номером {phone_number} не найден")
            return
    
    user_id = user.get("id")
    
    if not user_id:
        await message.answer(str(UserNotExistsException(UserNotExistsException.__doc__)))
        return
    
    role = user.get("role")
    
    if role == "user":
        if not user.get("hashed_psw"):
            sent = await message.answer("Установите пароль для безопасности",
                                    reply_markup= await BackButtons.back_to_phone())
                
            await state.update_data(phone=phone_number, user_id=user["id"], last_bot_message=sent.message_id)
            await state.set_state(CustomerAuth.set_password)
                
        else:
            sent = await message.answer("Введите пароль для потдверждения доступа", 
                                            reply_markup=await BackButtons.back_to_phone())
                
            await state.update_data(phone=phone_number, user_id=user["id"], last_bot_message=sent.message_id)
            await state.set_state(CustomerAuth.enter_password)
            
    if role == "admin":
        if not user.get("hashed_psw"):
            sent = await message.answer("Установите пароль для безопасности", 
                                        reply_markup= await BackButtons.back_to_phone())
            await state.update_data(phone=phone_number, admin_id=user["id"], last_bot_message=sent.message_id)
            await state.set_state(AdminAuth.set_password)
            
        else:
            sent = await message.answer("Введите пароль для потдверждения доступа", 
                                        reply_markup=await BackButtons.back_to_phone())
            await state.update_data(phone=phone_number, admin_id=user["id"], last_bot_message=sent.message_id)
            await state.set_state(AdminAuth.enter_password)