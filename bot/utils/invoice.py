from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from bot.utils.bot_utils import BotUtils
from bot.states.invoice import InvoiceForm
from bot.states.invoice import INVOICE_STATE
from bot.keyboards.admin import AdminKeyboards
from bot.keyboards.customer import CustomerKeyboards

import asyncio
from typing import Union


class StateUtils():
    """
    Управление состоянием пользователя в Telegram-боте.
    """
    
    @classmethod
    async def get_summary(cls, message: Message, data: dict):
        """
        Отправляет пользователю сводку введённых данных.

        Args:
            message (Message): Объект входящего сообщения Telegram.
            data (dict): Словарь с данными накладной.

        Returns:
            Message: Отправленное сообщение с сводкой.
        """
        
        summary = (
            f"📦 <b>Перед отправкой проверьте данные внимательно!</b>\n\n"
            f"📄 Номер договора: {data.get('contract_number')}\n"
            f"🚚 Город отправления: {data.get('departure_city')}\n"
            f"🏠 Адрес отправления: {data.get('departure_address')}\n"
            f"📞 Номер получателя: {data.get('recipient_phone')}\n"
            f"🏙️ Город получателя: {data.get('recipient_city')}\n"
            f"🏡 Адрес доставки: {data.get('recipient_address')}\n"
            f"💰 Сумма страхования: {data.get('insurance_amount')} ₽"
        )

        sent = await message.answer(summary, reply_markup=await CustomerKeyboards.edit_or_confirm(), parse_mode="HTML")
        
        return sent
    
    @classmethod
    async def send_summary(cls, message: Message | CallbackQuery, data: dict, chat_id: int):
        """
        Отправляет сводку с данными накладной в указанный чат.

        Args:
            message (Message | CallbackQuery): Объект для доступа к боту.
            data (dict): Данные накладной.
            chat_id (int): ID чата для отправки сообщения.

        Returns:
            Message | None: Отправленное сообщение или None, если chat_id не указан.
        """
        
        summary = (
            f"📦 <b>Создать накладную для @{data.get('user_full_name')}</b>\n\n"
            f"📄 Номер договора: {data.get('contract_number')}\n"
            f"🚚 Город отправления: {data.get('departure_city')}\n"
            f"🏠 Адрес отправления: {data.get('departure_address')}\n"
            f"📞 Номер получателя: {data.get('recipient_phone')}\n"
            f"🏙️ Город получателя: {data.get('recipient_city')}\n"
            f"🏡 Адрес доставки: {data.get('recipient_address')}\n"
            f"💰 Сумма страхования: {data.get('insurance_amount')} ₽"
        )

        if chat_id:
            
            sent = await message.bot.send_message(chat_id=chat_id, text=summary, parse_mode="HTML", reply_markup=await AdminKeyboards.send_answer())
        
        return sent
    
    
    @classmethod
    async def push_state_to_history(cls, state: FSMContext, new_state: InvoiceForm):
        """
        Добавляет новое состояние в историю для возможного отката.

        Args:
            state (FSMContext): Текущее состояние FSM.
            new_state (InvoiceForm): Новое состояние для добавления.
        """
        
        data = await state.get_data()
        history = data.get("state_history", [])
        history.append(new_state.state)
        await state.update_data(state_history=history)
    
    @classmethod
    async def pop_state_from_history(cls, state: FSMContext):
        """
        Откатывает состояние к предыдущему из истории.

        Args:
            state (FSMContext): Текущее состояние FSM.

        Returns:
            InvoiceForm | None: Предыдущее состояние или None, если истории нет.
        """
        
        data = await state.get_data()
        history = data.get("state_history", [])
        
        if history:
            history.pop()
            
            if history:
                prev_state = history[-1]
                
                for st in INVOICE_STATE:
                    if st.state == prev_state:
                        await state.set_state(st)
                        await state.update_data(state_history=history)
                        return st
                    
            else:
                await state.update_data(state_history=history)
                
        return None
    
    
    @classmethod
    async def prepare_next_state(cls, obj: Union[Message, CallbackQuery], state: FSMContext) -> dict:
        """
        Подготавливает и очищает сообщения перед переходом к следующему состоянию.

        Args:
            obj (Message | CallbackQuery): Объект входящего сообщения или callback.
            state (FSMContext): Текущее состояние FSM.

        Returns:
            dict: Текущие данные состояния.
        """
        
        await asyncio.sleep(0.3)
        
        data = await state.get_data()
        last_bot_message_id = data.get("last_bot_message")
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
            
        if message and last_bot_message_id:
            await BotUtils.delete_prev_messages(message, last_bot_message_id)
   
        return data
    
    
    @classmethod
    async def edit_invoice(cls, data: dict, message: Message, state: FSMContext):
        """
        Обрабатывает отмену редактирования поля накладной и обновляет сводку.

        Args:
            data (dict): Текущие данные состояния.
            message (Message): Объект сообщения для отправки обновлений.
            state (FSMContext): Текущее состояние FSM.

        Returns:
            bool: True, если было редактирование и оно завершено, иначе False.
        """
        
        if data.get("editing_field"):
            await state.update_data(editing_field=None)
            
            updated_data = await state.get_data()
            updated_summary = await StateUtils.get_summary(message, updated_data)
            
            await state.update_data(last_bot_message_id=updated_summary.message_id)
            await BotUtils.delete_prev_messages(message, updated_data.get("last_bot_message_id"))
            return True
        
        return False
            