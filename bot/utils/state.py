from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from app.core.config import settings
from bot.utils.bot_utils import BotUtils
from bot.states.invoice import InvoiceForm
from bot.states.invoice import INVOICE_STATE
from bot.states.customer import CUSTOMER_STATE
from bot.keyboards.admin import AdminKeyboards
from bot.keyboards.customer import CustomerKeyboards
from bot.utils.storage import AdminText, CustomerText

import asyncio
from typing import Union


# Объединяем множества состояний
ALL_STATES_SET = INVOICE_STATE | CUSTOMER_STATE  # множество объединенных состояний

# Строим словарь для быстрого поиска по строковому имени состояния
ALL_STATES = {state: state for state in ALL_STATES_SET}


class StateUtils():
    """
    Управление состоянием пользователя в Telegram-боте.
    """

    @classmethod
    async def show_customer_summary(cls, *, message: Message, data: dict):
        """
        Отправляет администратору сводку введённых данных по контрагенту.

        Args:
            message (Message): Объект входящего сообщения Telegram.
            data (dict): Словарь с данными контрагента.

        Returns:
            Message: Отправленное сообщение со сводкой.
        """
        
        
        summary = AdminText.NEW_CONTRACTOR_TEXT.format(
            contractor=data.get('contractor', 'Не указано'),
            city=data.get('city', 'Не указан'),
            contract_number=data.get('contract_number', 'Не указан'),
            phone=data.get('phone', 'Не указаны')
        )
        
        sent = await message.answer(summary, reply_markup=await AdminKeyboards.edit_or_confirm_customer(), parse_mode="HTML")
        
        return sent
    
    
    @classmethod
    async def format_contractor_summary(cls, *, message: Message, data: dict, for_admin: bool):
        """
        Отправляет пользователю сводку введённых данных.

        Args:
            message (Message): Объект входящего сообщения Telegram.
            data (dict): Словарь с данными накладной.

        Returns:
            Message: Отправленное сообщение со сводкой.
        """
        
        if for_admin:
            header = f"💼 <b>Связаться по поводу заключения договора с @{data.get('username')}!</b>"
        
        else:
            header = f"💼 <b>Перед отправкой проверьте данные внимательно!</b>"
        
        return CustomerText.CONTRACTOR_TEXT.format(
            header=header,
            tin_number=data.get('tin_number'),
            phone=data.get('phone')
        )

    
    @classmethod
    async def send_contractor_summary(cls, *, message: Message | CallbackQuery, data: dict, for_admin: bool):
        """
        Отправляет сводку с данными накладной в указанный чат.

        Args:
            message (Message | CallbackQuery): Объект для доступа к боту.
            data (dict): Данные накладной.
            chat_id (int): ID чата для отправки сообщения.

        Returns:
            Message: Отправленное сообщение в чат.
        """
        
        summary = await cls.format_contractor_summary(data=data, message=message, for_admin=for_admin)
        
        if for_admin:
            chat_id = settings.INVOICE_CHAT_ID        
            sent = await message.bot.send_message(chat_id=chat_id, text=summary, parse_mode="HTML")
        
        else:
            sent = await message.answer(summary, reply_markup=await CustomerKeyboards.edit_or_confirm_agreement(), parse_mode="HTML")

        return sent
        
        
    @classmethod
    async def format_summary(cls, *, message: Message, data: dict, for_admin: bool):
        """
        Отправляет пользователю сводку введённых данных.

        Args:
            message (Message): Объект входящего сообщения Telegram.
            data (dict): Словарь с данными накладной.

        Returns:
            Message: Отправленное сообщение со сводкой.
        """
        
        if for_admin:
            header = f"📦 <b>Создать накладную для @{data.get('username')}</b>"
        
        else:
            header = f"📦 <b>Перед отправкой проверьте данные внимательно!</b>"
        
        return CustomerText.INVOICE_TEXT.format(
            header=header,
            contract_number=data.get('contract_number'),
            departure_city=data.get('departure_city'),
            departure_address=data.get('departure_address'),
            recipient_phone=data.get('recipient_phone'),
            recipient_city=data.get('recipient_city'),
            recipient_address=data.get('recipient_address'),
            insurance_amount=data.get('insurance_amount'),
            extra=data.get('extra', 'Нет')
        )
    
    
    @classmethod
    async def send_summary(cls, *, message: Message | CallbackQuery, data: dict, for_admin: bool):
        """
        Отправляет сводку с данными накладной в указанный чат.

        Args:
            message (Message | CallbackQuery): Объект для доступа к боту.
            data (dict): Данные накладной.
            chat_id (int): ID чата для отправки сообщения.

        Returns:
            Message: Отправленное сообщение в чат.
        """
        
        summary = await cls.format_summary(data=data, for_admin=for_admin, message=message)

        if for_admin:
            chat_id = settings.INVOICE_CHAT_ID
            sent = await message.bot.send_message(chat_id=chat_id, text=summary, parse_mode="HTML", 
                                                  reply_markup=await AdminKeyboards.send_answer(user_id=data.get("user_id"), username=data.get("username")))
        else:
            sent = await message.answer(text=summary, reply_markup=await CustomerKeyboards.edit_or_confirm(), parse_mode="HTML")
        
        return sent
    
    
    @classmethod
    async def push_state_to_history(cls, *, state: FSMContext, new_state: InvoiceForm):
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
    async def pop_state_from_history(cls, *, state: FSMContext):
        """
        Откатывает состояние к предыдущему из истории.

        Args:
            state (FSMContext): Текущее состояние FSM.

        Returns:
            InvoiceForm.State | None: Предыдущее состояние или None, если истории нет.
        """
        
        data = await state.get_data()
        history = data.get("state_history", [])

        if not history:
            return None

        # Удаляем текущее состояние из истории
        history.pop()

        if not history:
            # Если после удаления истории нет — обновляем данные и возвращаем None
            await state.update_data(state_history=history)
            return None

        prev_state_str = history[-1]
        prev_state = ALL_STATES.get(prev_state_str)


        if prev_state is None:
            # Если состояние не найдено — очистить историю, вернуть None
            await state.update_data(state_history=[])
            return None

        # Устанавливаем предыдущее состояние и обновляем историю
        await state.set_state(prev_state)
        await state.update_data(state_history=history)

        return prev_state

    
    @classmethod
    async def prepare_next_state(cls, *, obj: Union[Message, CallbackQuery], state: FSMContext) -> dict:
        """
        Подготавливает и очищает сообщения перед переходом к следующему состоянию.

        Args:
            obj (Message | CallbackQuery): Объект входящего сообщения или callback.
            state (FSMContext): Текущее состояние FSM.

        Returns:
            dict: Текущие данные состояния.
        """
        
        await asyncio.sleep(0.1)
        
        data = await state.get_data()
        last_bot_message_id = data.get("last_bot_message")
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
            
        if message:
            if last_bot_message_id:
                await BotUtils.delete_prev_messages(obj=message, message_id=last_bot_message_id)
            if error_message_id:
                await BotUtils.delete_prev_messages(obj=message, message_id=error_message_id)
   
        return data
    
    
    @classmethod
    async def edit_invoice_or_data(cls, *, data: dict, message: Message, state: FSMContext):
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
            current_state = await state.get_state()
            
            if current_state and current_state.startswith("InvoiceForm:"):
                updated_summary = await StateUtils.send_summary(message=message, data=updated_data, for_admin=False)
            elif current_state and current_state.startswith("Contractor:"):
                updated_summary = await StateUtils.send_contractor_summary(message=message, data=updated_data, for_admin=False)
            elif current_state and current_state.startswith("Customer:") :
                updated_summary = await StateUtils.show_customer_summary(message=message, data=updated_data)            
            
            await state.update_data(last_bot_message_id=updated_summary.message_id)
            await BotUtils.delete_prev_messages(obj=message, message_id=updated_data.get("last_bot_message_id"))
            return True
        
        return False