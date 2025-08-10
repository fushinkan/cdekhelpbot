from aiogram.fsm.context import FSMContext
from aiogram.enums import ChatAction
from aiogram import filters, types
from aiogram import Router

from bot.middlewares.logging_middleware import LoggingMiddleware
from bot.middlewares.work_hours_middleware import WorkHoursMiddleware
from bot.keyboards.basic import BasicKeyboards
from bot.handlers.authorization.main_menu import proceed_to_main_menu
from bot.utils.storage import Welcome

import asyncio


router = Router()
router.message.middleware(LoggingMiddleware())
#router.message.middleware(WorkHoursMiddleware())


@router.message(filters.CommandStart(), flags={"data": True})
async def cmd_start(message: types.Message, state: FSMContext, **data: dict):
    """
    Обработчик команды /start.

    Отправляет приветственное сообщение пользователю и предлагает выбрать действие:
        - Войти: начать процесс авторизации.
        - Помощь: получить информацию о возможностях бота.

    Args:
        message (types.Message): Входящее сообщение с командой /start от пользователя.
        state (FSMContext): Контейнер для хранения и управления текущим состоянием пользователя.
        **data (dict): Дополнительные данные, передаваемые из middleware.
    """

    await state.clear()
    
    is_logged = data.get("is_logged", False)
    role = data.get("role", None)
    user_obj = data.get("obj")
    phones = user_obj.get("phones") if user_obj else None
    
    if is_logged and user_obj:
        if role == "admin":
            
            await message.delete()
            sent = await proceed_to_main_menu(user_data=user_obj, message=message, state=state)
            await state.update_data(last_bot_message=sent.message_id)
            return
        
        elif role == "user":
            if phones and len(phones) > 0:
                await state.update_data(phone=user_obj["phones"][0]["number"])
            else:
                await state.update_data(phone=None)

            await message.delete()
            sent = await proceed_to_main_menu(user_data=user_obj, message=message, state=state)
            await state.update_data(last_bot_message=sent.message_id)
            return

    welcoming_text = Welcome.WELCOME
    
    
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    await asyncio.sleep(1)    
    
    await message.answer(welcoming_text, reply_markup=await BasicKeyboards.get_welcoming_kb())
    
    await asyncio.sleep(1)
    await message.delete()


@router.message(filters.Command("chat_id"))
async def chat_id(message: types.Message):
    """
    Обработчик команды /chat_id.

    Отвечает сообщением с уникальным идентификатором Telegram-чата, из которого было отправлено сообщение.

    Args:
        message (types.Message): Входящее сообщение от пользователя.
    """
    
    chat_id = message.chat.id
    await message.answer(f"ID: {chat_id}")