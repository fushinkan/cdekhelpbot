from aiogram.types import Message
from aiogram.fsm.context import FSMContext

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
    
 