import asyncio

from aiogram.fsm.context import FSMContext
from aiogram.enums import ChatAction
from aiogram import filters, types
from aiogram import Router

from bot.keyboards.customer import CustomerKeyboards
from bot.keyboards.admin import AdminKeyboards
from bot.utils.middlewares import LoggingMiddleware
from bot.keyboards.basic import BasicKeyboards

router = Router()
router.message.middleware(LoggingMiddleware())


@router.message(filters.CommandStart(), flags={"data": True})
async def cmd_start(message: types.Message, state: FSMContext, **data: dict):
    """
    Обработчик команды /start. Отправляет приветственное сообщение и предлагает действия.
    
    Показывает кнопки:
        - Войти (начать процесс авторизации)
        - Помощь (информация о возможностях бота)
    """
    
    await state.clear()
    
    
    is_logged = data.get("is_logged", False)
    role = data.get("role", None)
    user_obj = data.get("obj")
    
    
    if is_logged and user_obj:
        
        if role == "admin":
            sent = await message.answer((
                f"👋 Здравствуйте, {user_obj.contractor}\n\n"
                "Добро пожаловать в панель управления.\n"
                "Здесь вы можете управлять пользователями и контролировать систему.\n"
                "Выберите нужный пункт меню, чтобы начать работу."
            ), reply_markup=await AdminKeyboards.get_admin_kb())
            return
        
        elif role == "user":
            await state.update_data(phone=user_obj.phones[0].number)
            
            sent = await message.answer((
                "👋 Приветствую!\n\n"
                "Здесь ты можешь быстро оформить накладную, подобрать тарифы и подключить дополнительные услуги. 🚀\n"
                "Не нужно ломать голову — просто выбери, что нужно, и я всё сделаю быстро и без лишних хлопот! 💼✨\n"
                "Если возникнут вопросы — пиши, всегда рад помочь! 😊👍"
            ), reply_markup=await CustomerKeyboards.customer_kb())
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
    chat_id = message.chat.id
    await message.answer(f"ID: {chat_id}")