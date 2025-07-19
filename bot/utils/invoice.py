import asyncio

from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from bot.utils.bot_utils import BotUtils
from bot.keyboards.customer import CustomerKeyboards
from bot.states.invoice import InvoiceForm
from bot.states.invoice import INVOICE_STATE
from bot.keyboards.admin import AdminKeyboards

from typing import Union

class StateUtils():
    """
    Управление состоянием.
    """
    
    @classmethod
    async def get_summary(cls, message: Message, data: dict):
        """
        Показывает пользователю сводку его введенных данных.
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
        Отправляет сводку в чат для создания накладных.
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
        Записывает состояние в историю, для отката состояния на предыдущий этап.
        """
        data = await state.get_data()
        history = data.get("state_history", [])
        history.append(new_state.state)
        await state.update_data(state_history=history)
    
    @classmethod
    async def pop_state_from_history(cls, state: FSMContext):
        """
        Откатывает состояния до предыдущего этапа.
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
        Подготовка следующего состояния.
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
        Проверяет идет ли редактирование пункта.
        """
        
        if data.get("editing_field"):
            await state.update_data(editing_field=None)
            updated_data = await state.get_data()
            updated_summary = await StateUtils.get_summary(message, updated_data)
            await state.update_data(last_bot_message_id=updated_summary.message_id)
            await BotUtils.delete_prev_messages(message, updated_data.get("last_bot_message_id"))
            return True
        
        return False
            