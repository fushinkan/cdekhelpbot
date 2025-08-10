from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

class SettingsKeyboards:
    """Клавиатуры для настроек"""
    
    @classmethod
    async def main_keyboard(cls, *, user_data: dict):
        """
        По нажатию на кнопку 'Настройки' показывает меню настроек

        Args:
            user_data (dict): Данные пользователя для возврата в главное меню
            
        Returns:
            InlineKeyboardMarkup: Клавиатура настроек.
        """

        callback_data = "admin_panel" if user_data.get("role") == "admin" else "go_back_to_menu"
        
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔑 Сменить пароль", callback_data="change_password")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data=callback_data)]
        ])