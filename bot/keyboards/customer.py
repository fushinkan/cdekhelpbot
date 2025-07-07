from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

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
            [InlineKeyboardButton(text="✍️ Договор", callback_data="create_agreement"), InlineKeyboardButton(text="➕ Услуги", callback_data="services")],
            [InlineKeyboardButton(text="💰 Тарифы", callback_data="tariffs")],
            [InlineKeyboardButton(text="🎁 Получить мерч", callback_data="get_merch")],
            [InlineKeyboardButton(text="⚙ Настройки", callback_data="settings")],
            [InlineKeyboardButton(text="🚪 Выйти", callback_data="back_to_welcoming_screen")]
        ])
        
    @classmethod
    async def edit_or_confirm(cls):
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✏️ Город отправления", callback_data="edit_departure_city"), InlineKeyboardButton(text="✏️ Город получателя", callback_data="edit_recipient_city")],
            [InlineKeyboardButton(text="✏️ Адрес отправления", callback_data="edit_departure_address"), InlineKeyboardButton(text="✏️ Адрес доставки", callback_data="edit_recipient_address")],
            [InlineKeyboardButton(text="✏️ Телефон получателя", callback_data="edit_recipient_phone"), InlineKeyboardButton(text="✏️ Сумма страховки", callback_data="edit_insurance_amount")],
            
            [InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm"), 
             InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
        ])
        
        
    @classmethod
    async def extra_services(cls):
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Да", callback_data="yes"), InlineKeyboardButton(text="❌ Нет", callback_data="no")]
        ])