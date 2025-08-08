from aiogram.types import Message

from bot.keyboards.admin import AdminKeyboards
from bot.keyboards.customer import CustomerKeyboards


async def proceed_to_main_menu(*, role: str, user_data: dict, message: Message):
    """
    Главное меню для пользователя/админа в зависимости от role в БД.

    Args:
        obj (Users | Admins): ORM модель Users/Admins в зависимости от роли, полученная из БД.
        message (Message): Объект входящего Telegram-сообщения от пользователя.

    Returns:
        Message: Ответное сообщение, отправленное пользователю с соответствующей клавиатурой для его роли. 
    """
    
    if role == "admin":
        sent = await message.answer((
            f"👋 Отдел сопровождения\n\n"
            "Добро пожаловать в панель управления.\n"
            "Здесь вы можете просматривать клиентов, их историю заказов, тарифы и услуги, а также управлять доступом.\n"
            "Выберите нужный пункт меню, чтобы начать работу."
        ), reply_markup=await AdminKeyboards.get_admin_kb())
           
    else:
        sent = await message.answer((
            "👋 Привет!\n\n"
            "Здесь ты можешь:\n"
            "📦 Создавать накладные и просматривать историю заказов\n"
            "📜 Изучать информацию о тарифах и дополнительных услугах\n"
            "🎁 Получить мерч\n\n"
            "⚙️ В настройках можно изменить пароль в любое время.\n\n"
            "💬 Если нужна помощь — всегда можешь написать в Telegram @CDEK48\n"
            "📞 Или позвонить/написать в WhatsApp по номеру +7-951-305-30-36\n\n"
            "Действуй — всё просто и удобно! 🚀"
        ), reply_markup=await CustomerKeyboards.customer_kb())
        
    return sent