from aiogram.fsm.context import FSMContext
from aiogram import Router
from aiogram.types import Message


from bot.states.invoice import InvoiceForm
from bot.keyboards.backbuttons import BackButtons
from bot.utils.invoice import StateUtils
from bot.utils.bot_utils import BotUtils

router = Router()
    
    
@router.message(InvoiceForm.recipient_address)
async def get_recipient_address(message: Message, state: FSMContext):
    """
    Обрабатывает ввод адреса доставки в рамках формы InvoiceForm.

    Args:
        message (Message): Входящее сообщение с адресом доставки от пользователя.
        state (FSMContext): Контейнер для хранения и управления состоянием пользователя в процессе заполнения формы.
    """
    
    data = await StateUtils.prepare_next_state(message, state)
    recipient_address = message.text.strip()
    
    await state.update_data(recipient_address=recipient_address)
    
    if await StateUtils.edit_invoice(data, message, state):
        return
    
    await state.set_state(InvoiceForm.insurance_amount)
    await StateUtils.push_state_to_history(state, InvoiceForm.insurance_amount)
    
    sent = await message.answer("🛡️ На какую сумму нужна страховка?", reply_markup=await BackButtons.back_to_recipient_address())
    
    await state.update_data(last_bot_message=sent.message_id)
    
