from aiogram.types import Message

from bot.keyboards.admin import AdminKeyboards
from bot.keyboards.customer import CustomerKeyboards
from bot.utils.storage import AdminText, CustomerText


async def proceed_to_main_menu(*, user_data: dict, message: Message):
    """
    Главное меню для пользователя/админа в зависимости от role в БД.

    Args:
        obj (Users | Admins): ORM модель Users/Admins в зависимости от роли, полученная из БД.
        message (Message): Объект входящего Telegram-сообщения от пользователя.

    Returns:
        Message: Ответное сообщение, отправленное пользователю с соответствующей клавиатурой для его роли. 
    """
    
    if user_data.get("role") == "admin":
        sent = await message.answer(AdminText.WELCOME, reply_markup=await AdminKeyboards.get_admin_kb(), parse_mode="HTML")
           
    else:
        sent = await message.answer(CustomerText.WELCOME, reply_markup=await CustomerKeyboards.customer_kb(), parse_mode="HTML")
        
    return sent