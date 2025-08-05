from aiogram.fsm.context import FSMContext
from aiogram.enums import ChatAction
from aiogram import filters, types
from aiogram import Router, F

from bot.keyboards.customer import CustomerKeyboards
from bot.keyboards.admin import AdminKeyboards
from bot.middlewares.logging_middleware import LoggingMiddleware
from bot.middlewares.work_hours_middleware import WorkHoursMiddleware
from bot.keyboards.basic import BasicKeyboards

import asyncio


router = Router()
router.message.middleware(LoggingMiddleware())
router.message.middleware(WorkHoursMiddleware())


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
            
            sent = await message.answer((
                f"👋 Здравствуйте, {user_obj["contractor"]}\n\n"
                "Добро пожаловать в панель управления.\n"
                "Здесь вы можете управлять пользователями и контролировать систему.\n"
                "Выберите нужный пункт меню, чтобы начать работу."
            ), reply_markup=await AdminKeyboards.get_admin_kb())
            
            await asyncio.sleep(1)
            await message.delete()
            
            return
        
        elif role == "user":
            if phones and len(phones) > 0:
                await state.update_data(phone=user_obj["phones"][0]["number"])
            else:
                await state.update_data(phone=None)
                
            sent = await message.answer((
                "👋 Приветствую!\n\n"
                "Здесь ты можешь быстро оформить накладную, подобрать тарифы и подключить дополнительные услуги. 🚀\n"
                "Не нужно ломать голову — просто выбери, что нужно, и я всё сделаю быстро и без лишних хлопот! 💼✨\n"
                "Если возникнут вопросы — пиши, всегда рад помочь! 😊👍"
            ), reply_markup=await CustomerKeyboards.customer_kb())
            
            await asyncio.sleep(1)
            await message.delete()
            
            return

    welcoming_text = (
        "👋 Привет!\n\n"
        "Я — электронный помощник менеджера по продажам СДЭК.\n\n"
        "Работаю по адресу:\n" 
        "Липецкая область, г. Данков,\n 1-й Спортивный переулок, 3\n\n"
        "Выбери нужный пункт меню, чтобы начать работу."
    )
    
    
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
    
@router.message(F.document)
async def get_document_id(message: types.Message):
    file_id = message.document.file_id
    await message.answer(file_id)