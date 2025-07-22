from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery


class BackButtons:
    """
    Кнопки 'Назад'
    """
    
    @classmethod
    async def get_back_button(cls, callback_data: str, text: str = "⬅️ Назад") -> InlineKeyboardMarkup:
        """
        Создаёт и возвращает кнопку 'Назад' с заданным текстом и callback_data.

        Args:
            callback_data (str): Данные callback-запроса, которые будут отправлены при нажатии кнопки.
            text (str, optional): Текст, отображаемый на кнопке. По умолчанию "⬅️ Назад".

        Returns:
            InlineKeyboardMarkup: Объект клавиатуры с кнопкой 'Назад' для отправки в Telegram.
        """
        
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=text, callback_data=callback_data)]
        ])
    
    @classmethod
    async def back_to_welcoming_screen(cls):
        """
        Формирует клавиатуру для возврата к приветственному экрану.

        Returns:
            InlineKeyboardMarkup: Клавиатура с кнопками приветственного меню.
        """
        
        return await cls.get_back_button(callback_data="back_to_welcoming_screen")
    
    @classmethod 
    async def back_to_phone(cls):
        """
        Формирует клавиатуру для возврата к этапу ввода номера телефона при авторизации.

        Returns:
            InlineKeyboardMarkup: Клавиатура с кнопкой для возврата к вводу номера телефона.
        """
        
        return await cls.get_back_button(callback_data="back_to_phone")
    
    @classmethod
    async def go_back_to_phone(cls):
        """
        Формирует клавиатуру для возврата к этапу ввода номера телефона получателя.

        Returns:
            InlineKeyboardMarkup: Клавиатура с кнопкой для возврата к вводу номера телефона получателя при изменение общей сводки.
        """ 
        
        return await cls.get_back_button(callback_data="go_back_to_phone")
    
    @classmethod
    async def back_to_menu(cls):
        """
        Формирует клавиатуру для возврата в главное меню.

        Returns:
            InlineKeyboardMarkup: Клавиатура с кнопкой для возврата в главное меню.
        """
        
        return await cls.get_back_button(callback_data="go_back_to_menu")
    
    @classmethod
    async def back_to_departure_city(cls):
        """
        Формирует клавиатуру для возврата к этапу выбора города отправления.

        Returns:
            InlineKeyboardMarkup: Клавиатура с кнопкой для возврата к выбору города отправления.
        """
        
        return await cls.get_back_button(callback_data="go_back_to_city")
    
    @classmethod
    async def back_to_departure_address(cls):
        """
        Формирует клавиатуру для возврата к этапу выбора адреса отправления.

        Returns:
            InlineKeyboardMarkup: Клавиатура с кнопкой для возврата к выбору адреса отправления.
        """
        
        return await cls.get_back_button(callback_data="go_back_to_address")
    
    @classmethod
    async def back_to_recipient_phone(cls):
        """
        Формирует клавиатуру для возврата к этапу ввода телефона получателя.

        Returns:
            InlineKeyboardMarkup: Клавиатура с кнопкой для возврата к вводу телефона получателя.
        """
        
        return await cls.get_back_button(callback_data="go_back_to_recipient_phone")
    
    @classmethod
    async def back_to_recipient_city(cls):
        """
        Формирует клавиатуру для возврата к этапу выбора города получателя.

        Returns:
            InlineKeyboardMarkup: Клавиатура с кнопкой для возврата к выбору города получателя.
        """
        
        return await cls.get_back_button(callback_data="go_back_to_recipient_city")
    
    @classmethod
    async def back_to_recipient_address(cls):
        """
        Формирует клавиатуру для возврата к этапу выбора адреса получателя.

        Returns:
            InlineKeyboardMarkup: Клавиатура с кнопкой для возврата к выбору адреса получателя.
        """
        
        return await cls.get_back_button(callback_data="go_back_to_recipient_address")
    
    @classmethod
    async def back_to_summary(cls):
        """
        Формирует клавиатуру для возврата к сводке заказа.

        Returns:
            InlineKeyboardMarkup: Клавиатура с кнопкой для возврата к сводке заказа.
        """
            
        return await cls.get_back_button(callback_data="back_to_summary")
    
    @classmethod
    async def back_to_contractor_phone(cls):
        """
        Формирует клавиатуру для возврата к этапу ввода номера телефона для заключения договора.

        Returns:
            InlineKeyboardMarkup: Клавиатура с кнопкой для возврата к этапу ввода номера телефона для заключения договора.
        """
        
        return await cls.get_back_button(callback_data="back_to_contractor_phone")
    
    @classmethod
    async def back_to_contractor_summary(cls):
        """
        Формирует клавиатуру для возврата сводке с данными пользователя.

        Returns:
            InlineKeyboardMarkup: Клавиатура с кнопкой для возврата к сводке с данными пользователя.
        """
        
        return await cls.get_back_button(callback_data="back_to_contractor_summary")