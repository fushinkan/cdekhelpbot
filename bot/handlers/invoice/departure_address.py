from aiogram.fsm.context import FSMContext
from aiogram import F, Router
from aiogram.types import Message


from bot.states.invoice import InvoiceForm
from bot.keyboards.backbuttons import BackButtons
from bot.utils.invoice import StateUtils
from bot.utils.delete_messages import delete_prev_messages

router = Router()


@router.message(InvoiceForm.departure_address)
async def get_departure_address(message: Message, state: FSMContext):
    """
    Обработчик для адреса отправления.
    """

    data = await StateUtils.prepare_next_state(message, state)
    
    
    departure_address = message.text.strip()
    await state.update_data(departure_address=departure_address)
    
    
    if data.get("editing_field"):
        await state.update_data(editing_field=None)
        updated_data = await state.get_data()
        updated_summary = await StateUtils.get_summary(message, updated_data)
        await state.update_data(last_bot_message_id=updated_summary.message_id)
        await delete_prev_messages(message, updated_data.get("last_bot_message_id"))
        return
    
    
    await state.set_state(InvoiceForm.recipient_phone)
    await StateUtils.push_state_to_history(state, InvoiceForm.recipient_phone)
    
    
    sent = await message.answer("📱 Введите номер телефона получателя", reply_markup=await BackButtons.back_to_departure_address())
    
    
    await state.update_data(last_bot_message=sent.message_id)
