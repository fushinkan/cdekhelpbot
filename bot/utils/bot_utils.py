import asyncio
from typing import Union

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest

class BotUtils:
    """
    Класс с дополнительными утилитами для работы с ботом.
    """
    
    @classmethod
    async def delete_prev_messages(cls, *, obj: Union[Message, CallbackQuery], message_id: int):
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
    
           
    @classmethod
    async def delete_error_messages(cls, *, obj: Union[Message, CallbackQuery], state: FSMContext) -> dict:
        """
        Удаляет сообщения об ошибках при некорректном вводе.

        Args:
            obj (Message | CallbackQuery): Объект входящего сообщения или callback.
            state (FSMContext): Текущее состояние FSM.

        Returns:
            dict: Текущие данные состояния.
        """
        
        await asyncio.sleep(0.3)
        
        data = await state.get_data()
        error_message_id = data.get("error_message")
        message = None
        
        if isinstance(obj, CallbackQuery):
            await obj.answer()
            
            try:
                await obj.message.delete()
                
            except TelegramBadRequest:
                pass
            
            message = obj.message
            
        else:
            try:
                await obj.delete()    
                  
            except TelegramBadRequest:
                pass
            
            message = obj  
            
        if message and error_message_id:
            await BotUtils.delete_prev_messages(obj=message, message_id=error_message_id)
   
        return data