import asyncio

from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.utils.delete_messages import delete_prev_messages
from bot.keyboards.customer import CustomerKeyboards
from bot.states.invoice import InvoiceForm
from bot.states.invoice import INVOICE_STATE

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
    async def handle_step(
        message: Message,
        state: FSMContext,
        field_name: str,
        next_state,
        prompt_text: str,
        back_keyboard,
        validator=None
    ):
        data = await state.get_data()
        last_bot_message_id = data.get("last_bot_message")
        value = message.text.strip()

        # Валидация
        if validator:
            try:
                await validator(value)
            except Exception as e:
                sent = await message.answer(str(e), parse_mode="HTML")
                await asyncio.sleep(5)
                await sent.delete()
                await message.delete()
                return

        await asyncio.sleep(0.3)
        await message.delete()
        await delete_prev_messages(message, last_bot_message_id)

        await state.update_data({field_name: value})
        await state.set_state(next_state)
        await StateUtils.push_state_to_history(state, next_state)

        sent = await message.answer(prompt_text, reply_markup=await back_keyboard())
        await state.update_data(last_bot_message=sent.message_id)