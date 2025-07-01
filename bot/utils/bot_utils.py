from typing import Union

from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest


class BotUtils:
    """
    Дополнительные возможности бота.
    """
    
    @classmethod
    async def delete_prev_messages(cls, obj: Union[Message, CallbackQuery], message_id: int):
        """
        Удаляет сообщение бота. 
        
        Принимает либо Message либо CallbackQuery.
        """
        if isinstance(obj, Message):
            chat_id = obj.chat.id
        elif isinstance(obj, CallbackQuery):
            chat_id = obj.message.chat.id
        
        try:
            await obj.bot.delete_message(chat_id=chat_id, message_id=message_id)
        except TelegramBadRequest as e:
            pass