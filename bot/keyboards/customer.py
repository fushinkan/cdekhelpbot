from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from datetime import datetime


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
            [InlineKeyboardButton(text="📜 История заказов", callback_data="history")],
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
            [InlineKeyboardButton(text="✏️ ИНН", callback_data="edit_contractor_tin_number"), InlineKeyboardButton(text="✏️ Номер телефона", callback_data="edit_contractor_phone")],
            [InlineKeyboardButton(text="✅ Заключить договор", callback_data="allow_agreement"), InlineKeyboardButton(text="❌ Отмена", callback_data="back_to_welcoming_screen")]
        ])
        
    
    @classmethod
    async def get_main_titles(cls, *, titles: list[str], callback_prefix: str, data: dict):
        """
        По нажатию на кнопку 'Тарифы' формирует клавиатуру с кнопками-тарифами

        Args:
            titles (list[str]): Список основных тарифов.
            callback_prefix (str): Префикс для обработки кнопок с помощью CallbackQuery.
            data (dict): user_data для возврата на главное меню (admin_panel или back_to_menu)

        Returns:
            InlineKeyboardBuilder: Клавиатура.
        """
        
        keyboard = InlineKeyboardBuilder()
        
        for title in titles:
            keyboard.add(
                InlineKeyboardButton(
                    text=title,
                    callback_data=f"{callback_prefix}:{title}"
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
    async def get_sub_titles(cls, *, subtitles: list[str], callback_prefix: str):
        """
        По нажатию на тариф 'Доставка до маркетплейсов' формирует клавиатуру с кнопками субтарифов.
        
        Args:
            subtitles (list[str]): Субтарифы.
            callback_prefix (str): Префикс для обработки кнопок с помощью CallbackQuery.

        Returns:
            InlineKeyboardBuilder: Клавиатура.
        """
        
        keyboard = InlineKeyboardBuilder()
        
        for sub in subtitles:
            keyboard.add(
                InlineKeyboardButton(
                    text=sub,
                    callback_data=f"{callback_prefix}:{sub}"
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
        """
        Возвращает пользователя к тарифу 'Доставка до маркетплейсов'.

        Args:
            parent_tariff (str): Доставка до маркетплейсов

        Returns:
            InlineKeyboardBuilder: Клавиатура
        """
        
        keyboard = InlineKeyboardBuilder()
        
        keyboard.add(
            InlineKeyboardButton(
                text=f"⬅️ Назад",
                callback_data=f"tariff:{parent_tariff}"
            )
        )
        
        return keyboard.as_markup()
    
    
    @classmethod
    async def get_years_keyboard(cls, *, years: list[int], data: dict):
        """
        По нажатию на кнопку 'История' формирует клавиатуру с кнопками-годами заказов для конкретного пользователя.

        Args:
            years (list[int]): Список с годами. [2025 и т.д.]
            data (dict): user_data для возврата на главное меню (admin_panel или back_to_menu)

        Returns:
            InlineKeyboardBuilder: Клавиатура.
        """
        
        keyboard = InlineKeyboardBuilder()
        
        for year in years:
            keyboard.add(
                InlineKeyboardButton(
                    text=str(year),
                    callback_data=f"year:{year}"
                )
            )
        
        callback_data = "admin_panel" if data.get("role") == "admin" else "back_to_menu"
        
        keyboard.row(
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=callback_data
            )
        )   
        
        return keyboard.adjust(1).as_markup()
    
    
    @classmethod
    async def get_months_by_year_keyboard(cls, *, months: list[int], year: int, data: dict):
        """
        По нажатию на какой либо год формирует клавиатуру с кнопками-месяцами заказов для конкретного пользователя.

        Args:
            months (list[int]): Список месяцев. [1, 2 и т.д.]
            year (int): Год заказа.
            data (dict): user_data для возврата на главное меню (admin_panel или back_to_menu)

        Returns:
            InlineKeyboardBuilder: Клавиатура.
        """
        
        keyboard = InlineKeyboardBuilder()
        
        month_names = {
            1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель",
            5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
            9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"
        }
        
        for month in months:
            keyboard.add(
                InlineKeyboardButton(
                    text=month_names.get(month, f"{'month'}"),
                    callback_data=f"month:{year}:{month}"
                )
            )
            
        keyboard.row(
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data="history"
            )
        )
        
        return keyboard.adjust(2).as_markup()


    @classmethod
    async def get_invoices_by_month_year_keyboard(cls, *, invoices: list[dict], year: int):
        """
        По нажатию на месяц формирует кнопки с накладными.

        Args:
            invoices (list[dict]): Список накладных за месяц, где каждый элемент
                содержит keys: departure_city, recipient_city, invoice_id.

        Returns:
            InlineKeyboardBuilder: Клавиатура.
        """

        keyboard = InlineKeyboardBuilder()

        for invoice in invoices:
            # Парсим дату из строки ISO
            dt = datetime.fromisoformat(invoice["created_at"])
            day = dt.day

            text = f"({day}) {invoice['departure_city']} - {invoice['recipient_city']}"
            keyboard.add(
                InlineKeyboardButton(
                    text=text,
                    callback_data=f"invoice:{invoice['invoice_id']}"
                )
            )

        # Кнопка "Назад"
        keyboard.row(
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=f"year:{year}"
            )
        )

        count = len(invoices)

        if count <= 2:
            keyboard.adjust(1)
        elif 3 <= count <= 6:
            keyboard.adjust(2)
        elif 7 <= count <= 12:
            keyboard.adjust(3)
        else:
            keyboard.adjust(4)

        return keyboard.as_markup()