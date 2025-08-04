from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

class CustomerKeyboards():
    """
    Клавиатуры для пользователя.
    """
    
    @classmethod
    async def password_kb(cls):
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔒 Установить пароль", callback_data="set_password"),
            InlineKeyboardButton(text="✅ Продолжить", callback_data="continue")],
        ])
    
    @classmethod  
    async def customer_kb(cls):
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📝 Накладная", callback_data="create_invoice"), InlineKeyboardButton(text="💬 Поддержка", callback_data="support")],
            [InlineKeyboardButton(text="💰 Тарифы", callback_data="tariffs"), InlineKeyboardButton(text="➕ Услуги", callback_data="services")],
            [InlineKeyboardButton(text="🎁 Получить мерч", callback_data="get_merch")],
            [InlineKeyboardButton(text="⚙ Настройки", callback_data="settings")],
            [InlineKeyboardButton(text="🚪 Выйти", callback_data="back_to_welcoming_screen")]
        ])
        
    @classmethod
    async def edit_or_confirm(cls):
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✏️ Город отправления", callback_data="edit_invoice_departure_city"), InlineKeyboardButton(text="✏️ Город получателя", callback_data="edit_invoice_recipient_city")],
            [InlineKeyboardButton(text="✏️ Адрес отправления", callback_data="edit_invoice_departure_address"), InlineKeyboardButton(text="✏️ Адрес доставки", callback_data="edit_invoice_recipient_address")],
            [InlineKeyboardButton(text="✏️ Телефон получателя", callback_data="edit_invoice_recipient_phone"), InlineKeyboardButton(text="✏️ Сумма страховки", callback_data="edit_invoice_insurance_amount")],
            
            [InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm"), 
             InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
        ])
        
        
    @classmethod
    async def extra_services(cls):
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Да", callback_data="yes"), InlineKeyboardButton(text="❌ Нет", callback_data="no")]
        ])
        
        
    @classmethod
    async def edit_or_confirm_agreement(cls):
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✏️ ИНН", callback_data="editt_contractor_tin_number"), InlineKeyboardButton(text="✏️ Номер телефона", callback_data="editt_contractor_phone")],
            [InlineKeyboardButton(text="✅ Заключить договор", callback_data="allow_agreement"), InlineKeyboardButton(text="❌ Отмена", callback_data="back_to_welcoming_screen")]
        ])
        
    
    @classmethod
    async def get_main_titles(cls, *, titles: list[str], data: dict):
        keyboard = InlineKeyboardBuilder()
        
        for title in titles:
            keyboard.add(
                InlineKeyboardButton(
                    text=title,
                    callback_data=f"tariff:{title}"
                )
            )
        
        callback_data = "admin_panel" if data.get("role") == "admin" else "back_to_menu"
        
        keyboard.row(
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=callback_data
            )
        )
        
        return keyboard.adjust(2).as_markup()
    
    
    @classmethod
    async def get_sub_titles(cls, *, subtitles: list[str]):
        keyboard = InlineKeyboardBuilder()
        
        for sub in subtitles:
            keyboard.add(
                InlineKeyboardButton(
                    text=sub,
                    callback_data=f"subtariff:{sub}"
                )
            )
        
        keyboard.row(
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data="tariffs"
            )
        )    
            
        return keyboard.adjust(1).as_markup()
    
    
    @classmethod
    async def get_back_to_parent_tariff(cls, *, parent_tariff: str):
        keyboard = InlineKeyboardBuilder()
        
        keyboard.add(
            InlineKeyboardButton(
                text=f"⬅️ Назад",
                callback_data=f"tariff:{parent_tariff}"
            )
        )
        
        return keyboard.as_markup()
