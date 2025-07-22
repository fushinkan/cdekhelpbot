from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram import Router
from aiogram.types import Message


from bot.utils.validate import Validator
from bot.utils.exceptions import IncorrectInsurance
from bot.utils.state import StateUtils
from bot.states.invoice import InvoiceForm
from bot.keyboards.customer import CustomerKeyboards
from bot.utils.bot_utils import BotUtils


router = Router()


@router.message(InvoiceForm.insurance_amount)
async def get_insurance_amount(message: Message, state: FSMContext):
    """
    Обрабатывает ввод суммы страхования от пользователя.

    Args:
        message (Message): Входящее сообщение с суммой страхования.
        state (FSMContext): Контейнер для хранения и управления состоянием пользователя в процессе оформления.
    """
    
    data = await StateUtils.prepare_next_state(obj=message, state=state)
    insurance_amount = message.text.strip()
    await state.update_data(insurance_amount=insurance_amount)
    
    try:
        await Validator.correct_insurance(text=insurance_amount)
        
    except IncorrectInsurance as e:
        sent = await message.answer(str(e), parse_mode="HTML")
        await state.update_data(error_message=sent.message_id)
        return 
    
    if await StateUtils.edit_invoice_or_data(data=data, message=message, state=state):
        return
        
    data = await state.get_data()
    error_message = data.get("error_message")
    
    try:
        if error_message:
            await BotUtils.delete_prev_messages(obj=message, message_id=error_message)
            
    except TelegramBadRequest:
        pass    

    await state.set_state(InvoiceForm.confirmation)
    
    sent = await message.answer("🛠️ Добавить доп. услуги к заказу?", reply_markup=await CustomerKeyboards.extra_services())
    
    await state.update_data(last_bot_message=sent.message_id)
    