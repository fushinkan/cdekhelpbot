from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class BasicKeyboards():
    """
    Клавиатуры общего назначения.
    """
    
    @classmethod
    async def get_welcoming_kb(cls):
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👤 Войти", callback_data="enter"),
            InlineKeyboardButton(text="❓ Помощь", callback_data="help")]
        ])
        
