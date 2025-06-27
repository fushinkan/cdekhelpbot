from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery


class BackButtons:
    """
    Кнопки 'Назад'
    """
    
    @classmethod
    async def get_back_button(cls, callback_data: str, text: str = "⬅️ Назад") -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=text, callback_data=callback_data)]
        ])
    
    
    @classmethod
    async def back_to_welcoming_screen(cls):
        return await cls.get_back_button(callback_data="back_to_welcoming_screen")
        
    @classmethod
    async def back_to_phone(cls):    
        return await cls.get_back_button(callback_data="back_to_phone")
    
    @classmethod
    async def back_to_menu(cls):
        return await cls.get_back_button(callback_data="back_to_menu")
    
    @classmethod
    async def back_to_departure_city(cls):
        return await cls.get_back_button(callback_data="back_to_city")
    
    @classmethod
    async def back_to_departure_address(cls):
        return await cls.get_back_button(callback_data="back_to_address")
    
    @classmethod
    async def back_to_recipient_phone(cls):
        return await cls.get_back_button(callback_data="back_to_recipient_phone")
    
    @classmethod
    async def back_to_recipient_city(cls):
        return await cls.get_back_button(callback_data="back_to_recipient_city")
    
    @classmethod
    async def back_to_recipient_address(cls):
        return await cls.get_back_button(callback_data="back_to_recipient_address")