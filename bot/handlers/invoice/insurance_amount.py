from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram import Router
from aiogram.types import Message


from bot.utils.validate import InvoiceValidator
from bot.utils.exceptions import IncorrectInsurance
from bot.utils.invoice import StateUtils
from bot.states.invoice import InvoiceForm
from bot.keyboards.customer import CustomerKeyboards
from bot.utils.bot_utils import BotUtils


router = Router()


@router.message(InvoiceForm.insurance_amount)
async def get_insurance_amount(message: Message, state: FSMContext):
    """
    Обработчик для получения суммы страхования.
    """
    
    data = await StateUtils.prepare_next_state(message, state)
    insurance_amount = message.text.strip()
    await state.update_data(insurance_amount=insurance_amount)
    
    
    try:
        await InvoiceValidator.correct_insurance(insurance_amount)
    except IncorrectInsurance as e:
        sent = await message.answer(str(e), parse_mode="HTML")
        await state.update_data(error_message=sent.message_id)
        return 
    
    
    if await StateUtils.edit_invoice(data, message, state):
        return
        
        
    data = await state.get_data()
    error_message = data.get("error_message")
    try:
        if error_message:
            await BotUtils.delete_prev_messages(message, error_message)
    except TelegramBadRequest:
        pass    

    await state.set_state(InvoiceForm.confirmation)
    
    
    sent = await message.answer("🛠️ Добавить доп. услуги к заказу?", reply_markup=await CustomerKeyboards.extra_services())
    
    
    await state.update_data(last_bot_message=sent.message_id)
    