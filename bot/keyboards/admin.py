from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class AdminKeyboards():
    """
    Клавиатуры администратора.
    """
    
    @classmethod
    async def get_admin_kb(cls):
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👥 Пользователи", callback_data="customers"),
            InlineKeyboardButton(text="⚙ Настройки", callback_data="settings")],
            [InlineKeyboardButton(text="🚪 Выйти", callback_data="back_to_welcoming_screen")]
        ])
    
    @classmethod
    async def send_answer(cls):
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Ответить", callback_data="answer_to_client"),
             InlineKeyboardButton(text="Отменить", callback_data="reject_answer")]
        ])