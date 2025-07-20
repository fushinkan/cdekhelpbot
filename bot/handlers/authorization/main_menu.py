from aiogram.types import Message

from app.db.models.admins import Admins
from app.db.models.users import Users
from bot.keyboards.admin import AdminKeyboards
from bot.keyboards.customer import CustomerKeyboards


async def proceed_to_main_menu(obj: Users | Admins, message: Message):
    """
    Главное меню для пользователя/админа в зависимости от role в БД.

    Args:
        obj (Users | Admins): ORM модель Users/Admins в зависимости от роли, полученная из БД.
        message (Message): Объект входящего Telegram-сообщения от пользователя.

    Returns:
        Message: Ответное сообщение, отправленное пользователю с соответствующей клавиатурой для его роли. 
    """
    
    if isinstance(obj, Admins):
        sent = await message.answer((
            f"👋 Здравствуйте, {obj.contractor}\n\n"
            "Добро пожаловать в панель управления.\n"
            "Здесь вы можете управлять пользователями и контролировать систему.\n"
            "Выберите нужный пункт меню, чтобы начать работу."
        ), reply_markup=await AdminKeyboards.get_admin_kb())
           
    else:
        sent = await message.answer((
            "👋 Приветствую!\n\n"
            "Здесь ты можешь быстро оформить накладную, подобрать тарифы и подключить дополнительные услуги. 🚀\n"
            "Не нужно ломать голову — просто выбери, что нужно, и я всё сделаю быстро и без лишних хлопот! 💼✨\n"
            "Если возникнут вопросы — пиши, всегда рад помочь! 😊👍"
        ), reply_markup=await CustomerKeyboards.customer_kb())
        
    return sent
