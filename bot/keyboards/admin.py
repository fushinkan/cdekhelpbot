from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


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
            [InlineKeyboardButton(text="👥 Клиенты", callback_data="customers"), 
             InlineKeyboardButton(text="🆕 Добавить контрагента", callback_data="add_contractor")],
            [InlineKeyboardButton(text="💰 Тарифы", callback_data="tariffs"), InlineKeyboardButton(text="➕ Услуги", callback_data="services")],
            [InlineKeyboardButton(text="⚙ Настройки", callback_data="settings")],
            [InlineKeyboardButton(text="🚪 Выйти", callback_data="back_to_welcoming_screen")]
        ])


    @classmethod
    async def send_answer(cls, user_id: int, username: str):
        """Показывает клавиатуру в общем чате для создания накладных.
        
        Args:
            user_id (int): ID пользователя, которому отвечаем.
            username (str): Username пользователя, которому отвечаем.

        Returns:
            InlineKeyboardMarkup: Клавиатура для ответа из чата для создания накладных.
        """
        
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📤 Ответить", callback_data=f"answer_to_client:{user_id}:{username}"),
             InlineKeyboardButton(text="❌ Отменить", callback_data=f"reject_answer:{user_id}:{username}")]
        ])
        
        
    @classmethod
    async def get_customers(cls, *, clients: list[dict], page: int, total_pages: int) -> InlineKeyboardMarkup:
        """
        С помощью KeyboardBuilder'а создает клавиатуру с клиентами и кнопками пагинации.

        Args:
            clients (list): Список клиентов (объекты с атрибутами `.id` и `.contractor`)
            page (int): Текущая страница
            total_pages (int): Количество страниц

        Returns:
            InlineKeyboardMarkup: Клавиатура с клиентами и кнопками пагинации.
        """

        keyboard = InlineKeyboardBuilder()

        # Кнопки с клиентами
        for client in clients:
            keyboard.add(
                InlineKeyboardButton(
                    text=client["contractor"],
                    callback_data=f"client_{client["id"]}"
                )
            )

        # Пагинация
        pagination_buttons = []
        
        if page == 1:
            pagination_buttons.append(
                InlineKeyboardButton(
                    text="⬅️ Назад", callback_data="admin_panel"
                )
            )
        
        if page > 1:
            pagination_buttons.append(
                InlineKeyboardButton(
                    text="⬅️ Назад", callback_data=f"forward_page_{page - 1}"
                )
            )
            
        if page < total_pages:
            pagination_buttons.append(
                InlineKeyboardButton(
                    text="➡️ Вперёд", callback_data=f"backward_page_{page + 1}"
                )
            )

        if pagination_buttons:
            keyboard.row(*pagination_buttons)

        return keyboard.adjust(2).as_markup()
    
    
    @classmethod
    async def edit_or_confirm_customer(cls):
        """
        Клавиатура для редактирования сводки нового контрагента.

        Returns:
            InlineKeyboardMarkup: Клавиатура с кнопками для редактирования сводки контрагента.
        """
        
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✏️ Наименование контрагента", callback_data="edit_customer_contractor")],
            [InlineKeyboardButton(text="✏️ Город контрагента", callback_data="edit_customer_city")],
            [InlineKeyboardButton(text="✏️ Номер договора", callback_data="edit_customer_contract_number")],
            [InlineKeyboardButton(text="✏️ Номер(а) телефона", callback_data="edit_customer_number")],
            
            [InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_customer"), 
             InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_customer")]
        ])
        
    @classmethod
    async def back_to_customers_with_history(cls):
        """
        Показывает менеджеру подробную информацю о пользователе и дает возможность изменить пароль и просмотреть историю заказов.

        Args:
            user_id (int): ID пользователя из БД.

        Returns:
            InlineKeyboardMarkup: Клавиатура для просмотра подробной информации о пользователе.
        """
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📜 История заказов", callback_data=f"history"),
             InlineKeyboardButton(text="🔑 Сменить пароль", callback_data=f"change_password")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="customers")]
        ])
