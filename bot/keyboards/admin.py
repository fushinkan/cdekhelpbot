from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

class AdminKeyboards():
    """
    Клавиатуры администраторов.
    """
    
    @classmethod
    async def get_admin_kb(cls):
        """
        Показывает стартовую клавиатуру для админов.

        Returns:
            InlineKeyboardMarkup: Стартовая клавиатура для админов.
        """
        
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👥 Пользователи", callback_data="customers"),
            InlineKeyboardButton(text="⚙ Настройки", callback_data="settings")],
            [InlineKeyboardButton(text="🚪 Выйти", callback_data="back_to_welcoming_screen")]
        ])
    
    @classmethod
    async def send_answer(cls):
        """
        Показывает клавиатуру в общем чате для создания накладных.
        
        Returns:
            InlineKeyboardMarkup: Клавиатура для ответа из чата для создания накладных.
        """
        
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Ответить", callback_data="answer_to_client"),
             InlineKeyboardButton(text="Отменить", callback_data="reject_answer")]
        ])