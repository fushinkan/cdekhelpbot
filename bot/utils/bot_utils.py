from typing import Union

from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest

class BotUtils:
    """
    Класс с дополнительными утилитами для работы с ботом.
    """
    
    @classmethod
    async def delete_prev_messages(cls, obj: Union[Message, CallbackQuery], message_id: int):
        """
        Асинхронно удаляет предыдущее сообщение бота по заданному message_id.

        Args:
            obj (Union[Message, CallbackQuery]): Объект входящего сообщения или callback-запроса,
                из которого извлекается chat_id.
            message_id (int): ID сообщения, которое нужно удалить.

        Returns:
            None

        Примечания:
            - Если message_id равен None, функция просто завершает выполнение.
            - Обрабатывает исключения TelegramBadRequest и игнорирует их (например, если сообщение уже удалено).
        """
        
        if message_id is None:
            return
        
        if isinstance(obj, Message):
            chat_id = obj.chat.id
            
        elif isinstance(obj, CallbackQuery):
            chat_id = obj.message.chat.id
        
        try:
            await obj.bot.delete_message(chat_id=chat_id, message_id=message_id)
            
        except TelegramBadRequest as e:
            pass